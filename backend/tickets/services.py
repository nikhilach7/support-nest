import json
import logging
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)


class TicketClassifier:
    """
    Service for classifying support tickets using Gemini API
    """
    
    # Exact prompt used for classification
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
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel("gemini-1.5-flash")
    
    def classify(self, description):
        """
        Classify a ticket description using Gemini API
        
        Args:
            description (str): The ticket description to classify
            
        Returns:
            dict: Dictionary with 'suggested_category' and 'suggested_priority'
                  or None if classification fails
        """
        if not self.client or not self.api_key:
            logger.warning("Gemini API key not configured")
            return self._get_fallback_classification()

        # Heuristic override for common account/access issues
        lowered = description.lower()
        account_keywords = [
            "account", "login", "log in", "password", "reset", "authentication",
            "sign in", "sign-in", "signin", "cannot access", "can't access"
        ]
        if any(keyword in lowered for keyword in account_keywords):
            return {
                'suggested_category': 'account',
                'suggested_priority': 'medium'
            }
        
        try:
            # Call Gemini API
            prompt = self.CLASSIFICATION_PROMPT.format(description=description)
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 100
                }
            )
            
            # Parse response
            content = (response.text or "").strip()
            logger.info(f"Gemini response: {content}")
            
            # Extract JSON from response
            result = self._parse_classification_response(content)
            
            if result:
                return {
                    'suggested_category': result.get('category'),
                    'suggested_priority': result.get('priority')
                }
            else:
                logger.warning("Failed to parse Gemini response")
                return self._get_fallback_classification()
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return self._get_fallback_classification()
    
    def _parse_classification_response(self, content):
        """
        Parse the JSON response from Gemini
        
        Args:
            content (str): The response content
            
        Returns:
            dict or None: Parsed JSON or None if parsing fails
        """
        try:
            # Try to parse as JSON directly
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                json_str = content[json_start:json_end].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # Try to find JSON object in the text
            if '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            return None
    
    def _get_fallback_classification(self):
        """
        Return default classification when API fails
        
        Returns:
            dict: Default classification
        """
        return {
            'suggested_category': 'general',
            'suggested_priority': 'medium'
        }
