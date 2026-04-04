import json
import logging
import re
import time
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)


class TicketClassifier:
    """
    Service for classifying support tickets using Gemini API
    """

    CLASSIFICATION_PROMPT = """You are a support ticket classifier. Based on the ticket description provided, classify it into the appropriate category and priority.

Categories:
- billing: Issues related to payments, invoices, refunds, subscriptions
- technical: Technical problems, bugs, system errors, functionality issues
- account: Account access, login issues, password resets, profile issues, authentication
- general: General inquiries, questions, feedback, other

Priority Levels:
- low: General questions, minor issues, no immediate impact
- medium: Standard issues affecting user experience but have workarounds
- high: Significant issues affecting core functionality, no easy workaround
- critical: System down, security issues, data loss, affecting multiple users

Ticket Description: {description}

Important: If the description mentions login, password, authentication, account access, reset, or cannot access account, the category MUST be "account".

Respond with ONLY these two lines in plain text:
CATEGORY: one_of_the_categories
PRIORITY: one_of_the_priorities

Do not include markdown, code blocks, JSON, or extra text."""

    VALID_CATEGORIES = {"billing", "technical", "account", "general"}
    VALID_PRIORITIES = {"low", "medium", "high", "critical"}
    MAX_GEMINI_ATTEMPTS = 2
    RETRY_BACKOFF_SECONDS = 0.2

    PRIORITY_KEYWORDS = {
        "critical": ["data loss", "security", "breach", "system down", "down", "outage"],
        "high": ["cannot", "can't", "unable to", "no access", "payment failed", "urgent", "error", "crash"],
        "medium": ["slow", "problem", "issue", "bug", "not working", "fail"],
        "low": ["question", "help", "how to", "how do i", "feature request", "request"],
    }

    CATEGORY_KEYWORDS = {
        "billing": ["payment", "invoice", "refund", "charge", "subscription"],
        "technical": ["error", "bug", "crash", "slow", "timeout", "exception"],
        "account": ["account", "login", "password", "signin", "sign in", "authentication", "access"],
    }

    PREFERRED_MODELS = (
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro-latest",
        "gemini-pro",
    )

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        self.model_name = None

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model_name = self._resolve_model_name()
            self.client = genai.GenerativeModel(self.model_name)
            logger.info(f"Using Gemini model: {self.model_name}")

    def _resolve_model_name(self):
        configured_model = (getattr(settings, "GEMINI_MODEL", "") or "").strip()
        preferred = [configured_model] if configured_model else []
        preferred.extend(self.PREFERRED_MODELS)

        try:
            models = genai.list_models()
            available = {
                m.name.replace("models/", ""): m
                for m in models
                if "generateContent" in getattr(m, "supported_generation_methods", [])
            }

            for model_name in preferred:
                if model_name and model_name in available:
                    return model_name

            for model_name in available.keys():
                if model_name.startswith("gemini"):
                    return model_name
        except Exception as exc:
            logger.warning(f"Failed to list Gemini models, using default preference: {exc}")

        return preferred[0] if preferred else "gemini-1.5-flash"

    def classify(self, description):
        lowered = description.lower()

        account_keywords = [
            "account", "login", "log in", "password", "reset", "authentication",
            "sign in", "sign-in", "signin", "cannot access", "can't access", "no access",
        ]
        account_match = any(keyword in lowered for keyword in account_keywords)

        for level, keywords in self.PRIORITY_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                suggested_priority = level
                break
        else:
            suggested_priority = None

        if suggested_priority is None and ("?" in description or lowered.startswith("how ")):
            suggested_priority = "low"

        suggested_category = None
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                suggested_category = category
                break

        if account_match and suggested_category is None:
            suggested_category = "account"

        if not self.client or not self.api_key:
            logger.warning("Gemini API key not configured, using heuristic classification")
            return self._build_heuristic_result(suggested_category, suggested_priority)

        try:
            return self._classify_with_gemini(
                description=description,
                suggested_category=suggested_category,
                suggested_priority=suggested_priority,
                account_match=account_match,
            )
        except Exception as exc:
            logger.error(f"Gemini API failed, using heuristic fallback: {exc}")
            return self._build_heuristic_result(suggested_category, suggested_priority)

    def _classify_with_gemini(self, description, suggested_category, suggested_priority, account_match):
        prompt = self.CLASSIFICATION_PROMPT.format(description=description)
        result = None
        content = ""
        last_error = None
        logger.info(f"Starting Gemini classification for: {description[:80]}")

        for attempt in range(1, self.MAX_GEMINI_ATTEMPTS + 1):
            try:
                logger.info(f"Attempt {attempt}: Calling generate_content")
                response = self.client.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 256,
                    },
                )
                logger.info(f"Attempt {attempt}: Received response, extracting text")
                content = self._extract_response_text(response)
                logger.info(f"Attempt {attempt}: Extracted content (len={len(content)}): {content[:150]}")
                result = self._parse_classification_response(content)
                if result:
                    logger.info(f"Successfully parsed on attempt {attempt}: {result}")
                    break

                last_error = ValueError("Gemini response parsing failed")
                logger.warning(f"Gemini parsing failed on attempt {attempt}")
            except Exception as exc:
                last_error = exc
                logger.warning(f"Gemini request failed on attempt {attempt}: {exc}")

                # Non-retryable failures should fail fast to avoid noisy logs and wasted calls.
                if self._is_non_retryable_error(exc):
                    break

            if attempt < self.MAX_GEMINI_ATTEMPTS:
                time.sleep(self.RETRY_BACKOFF_SECONDS * attempt)

        if not result:
            # Gemini occasionally returns truncated JSON. Salvage useful fields if present.
            result = self._salvage_partial_classification(content)
            if not result:
                raise ValueError(str(last_error) if last_error else "Gemini response parsing failed")

        category = (result.get("category") or "").strip().lower()
        priority = (result.get("priority") or "").strip().lower()

        if category not in self.VALID_CATEGORIES:
            if suggested_category:
                category = suggested_category
            else:
                for fallback_category, keywords in self.CATEGORY_KEYWORDS.items():
                    if any(keyword in content.lower() for keyword in keywords):
                        category = fallback_category
                        break

        if priority not in self.VALID_PRIORITIES:
            if suggested_priority:
                priority = suggested_priority
            else:
                for fallback_priority, keywords in self.PRIORITY_KEYWORDS.items():
                    if any(keyword in content.lower() for keyword in keywords):
                        priority = fallback_priority
                        break

        if account_match:
            category = "account"

        if category not in self.VALID_CATEGORIES:
            category = "general"
        if priority not in self.VALID_PRIORITIES:
            priority = "medium"

        return {
            "suggested_category": category,
            "suggested_priority": priority,
            "classification_mode": "hybrid" if account_match else "gemini",
        }

    def _build_heuristic_result(self, suggested_category, suggested_priority):
        return {
            "suggested_category": suggested_category or "general",
            "suggested_priority": suggested_priority or "medium",
            "classification_mode": "heuristic",
        }

    def _parse_classification_response(self, content):
        """
        Parse JSON response from Gemini. Handles multiple formats:
        1. Plain JSON object
        2. JSON in markdown code blocks
        3. JSON embedded in text
        """
        if not content or not isinstance(content, str):
            logger.warning(f"Invalid content for parsing: {type(content)}")
            return None
        
        content = content.strip()
        
        # Attempt 1: Try parsing raw content
        try:
            result = json.loads(content)
            logger.debug(f"Parsed raw JSON successfully")
            return result
        except json.JSONDecodeError:
            logger.debug(f"Raw JSON parse failed")
        
        # Attempt 2: Extract from markdown code blocks (```json ... ```)
        if "```json" in content:
            try:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
                    result = json.loads(json_str)
                    logger.debug(f"Parsed JSON from markdown block successfully")
                    return result
            except (json.JSONDecodeError, ValueError) as e:
                logger.debug(f"Markdown JSON parse failed: {e}")
        
        # Attempt 3: Extract from generic code blocks (``` ... ```)
        if "```" in content:
            try:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
                    result = json.loads(json_str)
                    logger.debug(f"Parsed JSON from generic code block successfully")
                    return result
            except (json.JSONDecodeError, ValueError) as e:
                logger.debug(f"Generic code block parse failed: {e}")
        
        # Attempt 4: Find and extract JSON object {...}
        if "{" in content and "}" in content:
            try:
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                logger.debug(f"Parsed JSON from embedded object successfully")
                return result
            except (json.JSONDecodeError, ValueError) as e:
                logger.debug(f"Embedded JSON parse failed: {e}")

        # Attempt 5: Parse plain text format:
        # CATEGORY: account
        # PRIORITY: high
        category_match = re.search(r"category\s*:\s*([a-z]+)", content, flags=re.IGNORECASE)
        priority_match = re.search(r"priority\s*:\s*([a-z]+)", content, flags=re.IGNORECASE)
        if category_match or priority_match:
            parsed = {
                "category": (category_match.group(1).strip().lower() if category_match else ""),
                "priority": (priority_match.group(1).strip().lower() if priority_match else ""),
            }
            logger.debug("Parsed plain text category/priority format")
            return parsed
        
        # If nothing worked, log and return None
        logger.warning(f"Could not parse any JSON from response: {content[:200]}")
        return None

    def _salvage_partial_classification(self, content):
        if not content or not isinstance(content, str):
            return None

        lowered = content.lower()
        category = None
        priority = None

        category_match = re.search(r'"category"\s*:\s*"([a-z]+)"', lowered)
        priority_match = re.search(r'"priority"\s*:\s*"([a-z]+)"', lowered)

        if category_match:
            found = category_match.group(1)
            if found in self.VALID_CATEGORIES:
                category = found

        if priority_match:
            found = priority_match.group(1)
            if found in self.VALID_PRIORITIES:
                priority = found

        # If regex could not capture full values, infer from known labels in text.
        if not category:
            for candidate in self.VALID_CATEGORIES:
                if candidate in lowered:
                    category = candidate
                    break

        if not priority:
            for candidate in self.VALID_PRIORITIES:
                if candidate in lowered:
                    priority = candidate
                    break

        if not category and not priority:
            return None

        return {"category": category or "", "priority": priority or ""}

    def _is_non_retryable_error(self, exc):
        text = str(exc).lower()
        markers = [
            "api_key_invalid",
            "api key invalid",
            "api key not found",
            "api key expired",
            "resource_exhausted",
            "quota",
            "429",
        ]
        return any(marker in text for marker in markers)

    def _extract_response_text(self, response):
        text = ""
        
        # Try response.text attribute first (most common for Gemini models)
        try:
            if hasattr(response, 'text') and response.text:
                text = response.text.strip()
                if text:
                    logger.info(f"response.text (len={len(text)}): {text}")
                    return text
        except Exception as e:
            logger.debug(f"Failed to get response.text: {e}")
        
        # Try candidates structure (alternative response format)
        try:
            if hasattr(response, 'candidates') and response.candidates:
                parts = []
                for i, candidate in enumerate(response.candidates):
                    if hasattr(candidate, 'content') and candidate.content:
                        for j, part in enumerate(candidate.content.parts):
                            if hasattr(part, 'text'):
                                part_text = part.text
                                parts.append(part_text)
                                logger.debug(f"Candidate {i}, Part {j}: {part_text[:100]}")
                
                extracted = "".join(parts).strip()
                if extracted:
                    logger.info(f"Extracted from candidates (len={len(extracted)}): {extracted}")
                    return extracted
        except Exception as e:
            logger.debug(f"Failed to extract from candidates: {e}")
        
        # Try model_dump if it's a Pydantic model
        try:
            if hasattr(response, 'model_dump'):
                model_data = response.model_dump()
                logger.debug(f"Response model_dump keys: {list(model_data.keys())}")
                if 'text' in model_data:
                    text = model_data['text'].strip()
                    if text:
                        logger.info(f"Extracted from model_dump: {text[:100]}")
                        return text
        except Exception as e:
            logger.debug(f"Failed to extract from model_dump: {e}")
        
        # Last resort: return whatever we got
        logger.info(f"Returning fallback text (len={len(text) if text else 0})")
        return text