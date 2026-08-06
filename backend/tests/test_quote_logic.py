import unittest

from backend.quote_logic import build_quote_record, classify_quote, normalize_quote


class QuoteLogicTest(unittest.TestCase):
    def test_valid_high_priority_quote(self):
        quote, errors = build_quote_record(
            {
                "full_name": "Ana Perez",
                "email": "ana@example.com",
                "phone": "+57 300 123 4567",
                "customer_type": "empresa",
                "request_type": "quote",
                "product_category": "cable",
                "quantity": "150",
                "unit": "metro",
                "budget": "$2.500.000",
                "urgency": "hoy",
                "delivery_city": "Cucuta",
                "consent": True,
            }
        )

        self.assertEqual(errors, [])
        self.assertEqual(quote["priority"], "high")
        self.assertEqual(quote["status"], "qualified")
        self.assertEqual(quote["budget_cop"], 2500000)
        self.assertEqual(quote["product_category"], "cable")

    def test_validation_errors(self):
        quote, errors = build_quote_record(
            {
                "full_name": "",
                "email": "bad-email",
                "phone": "12",
                "product_category": "",
                "quantity": "0",
                "request_type": "quote",
                "consent": False,
            }
        )

        self.assertIn("valid email is required", errors)
        self.assertIn("valid phone is required", errors)
        self.assertIn("product_category is required", errors)
        self.assertIn("quantity is required for quotes", errors)
        self.assertNotIn("id", quote)

    def test_business_customer_is_medium_priority(self):
        quote = normalize_quote(
            {
                "full_name": "Luis",
                "email": "luis@example.com",
                "phone": "3001234567",
                "customer_type": "tecnico_electricista",
                "request_type": "question",
                "product_category": "lamparas",
                "quantity": "1",
                "urgency": "next_week",
                "consent": True,
            }
        )

        self.assertEqual(classify_quote(quote)["priority"], "medium")

    def test_small_quote_for_this_week_is_medium_priority(self):
        quote = normalize_quote(
            {
                "full_name": "Carlos",
                "email": "carlos@example.com",
                "phone": "3001234567",
                "customer_type": "persona",
                "request_type": "quote",
                "product_category": "lamparas",
                "quantity": "4",
                "urgency": "this_week",
                "consent": True,
            }
        )

        self.assertEqual(classify_quote(quote)["priority"], "medium")


if __name__ == "__main__":
    unittest.main()
