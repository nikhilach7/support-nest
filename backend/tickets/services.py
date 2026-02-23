import json
import logging
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

Respond with ONLY a JSON object in this exact format:
{{"category": "one_of_the_categories", "priority": "one_of_the_priorities"}}

Do not include any explanation or additional text."""

    VALID_CATEGORIES = {"billing", "technical", "account", "general"}
    VALID_PRIORITIES = {"low", "medium", "high", "critical"}

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

        for attempt in range(1, 4):
            try:
                response = self.client.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 256,
                        "response_mime_type": "application/json",
                    },
                )
                content = self._extract_response_text(response)
                logger.info(f"Gemini response (attempt {attempt}): {content}")
                result = self._parse_classification_response(content)
                if result:
                    break

                last_error = ValueError("Gemini response parsing failed")
                logger.warning(f"Gemini parsing failed on attempt {attempt}")
            except Exception as exc:
                last_error = exc
                logger.warning(f"Gemini request failed on attempt {attempt}: {exc}")

            if attempt < 3:
                time.sleep(1.2 * attempt)

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
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

            if "{" in content and "}" in content:
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

            return None

    def _extract_response_text(self, response):
        text = ""
        try:
            text = (response.text or "").strip()
        except Exception:
            text = ""

        if text and text != "```json":
            return text

        try:
            candidates = getattr(response, "candidates", []) or []
            parts = []
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                if not content:
                    continue
                for part in getattr(content, "parts", []) or []:
                    part_text = getattr(part, "text", "")
                    if part_text:
                        parts.append(part_text)

            extracted = "".join(parts).strip()
            return extracted or text
        except Exception:
            return text