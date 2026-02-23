from django.test import SimpleTestCase, override_settings

from tickets.services import TicketClassifier


@override_settings(GEMINI_API_KEY='')
class TicketClassifierTests(SimpleTestCase):
    def setUp(self):
        self.classifier = TicketClassifier()

    def test_account_access_detection_escalates(self):
        desc = "I cannot access my account after resetting my password."
        result = self.classifier.classify(desc)
        self.assertEqual(result['suggested_category'], 'account')
        self.assertEqual(result['suggested_priority'], 'high')

    def test_billing_payment_failed_high_priority(self):
        desc = "Payment failed when subscribing and I was charged twice, urgent refund required."
        result = self.classifier.classify(desc)
        self.assertEqual(result['suggested_category'], 'billing')
        self.assertEqual(result['suggested_priority'], 'high')

    def test_technical_crash_classified_high(self):
        desc = "App crashes with error 500 when uploading a file; no workaround available."
        result = self.classifier.classify(desc)
        self.assertEqual(result['suggested_category'], 'technical')
        self.assertEqual(result['suggested_priority'], 'high')

    def test_general_question_low_priority(self):
        desc = "How do I change my notification settings?"
        result = self.classifier.classify(desc)
        self.assertEqual(result['suggested_category'], 'general')
        self.assertEqual(result['suggested_priority'], 'low')
