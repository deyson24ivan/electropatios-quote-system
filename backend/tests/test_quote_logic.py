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
                "items": [
                    {
                        "sku": "CAB-THHN-12",
                        "name": "Cable THHN #12",
                        "category": "cable",
                        "quantity": "150",
                        "unit": "metro",
                    }
                ],
                "consent": True,
            }
        )

        self.assertEqual(errors, [])
        self.assertEqual(quote["priority"], "high")
        self.assertEqual(quote["status"], "qualified")
        self.assertEqual(quote["budget_cop"], 2500000)
        self.assertEqual(quote["product_category"], "cable")
        self.assertEqual(quote["items"][0]["sku"], "CAB-THHN-12")

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

        self.assertIn("valid_email_required", errors)
        self.assertIn("valid_phone_required", errors)
        self.assertIn("product_category_required", errors)
        self.assertIn("quantity_required_for_quotes", errors)
        self.assertIn("items_required_for_quotes", errors)
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

    def test_cart_with_multiple_categories_becomes_varios(self):
        quote, errors = build_quote_record(
            {
                "full_name": "Pedido Obra",
                "email": "obra@example.com",
                "phone": "3001234567",
                "customer_type": "empresa",
                "request_type": "quote",
                "urgency": "next_week",
                "items": [
                    {
                        "sku": "CAB-THHN-12",
                        "name": "Cable THHN #12",
                        "category": "cable",
                        "quantity": 30,
                        "unit": "metro",
                    },
                    {
                        "sku": "PRO-BRK-20A",
                        "name": "Breaker 20A",
                        "category": "proteccion",
                        "quantity": 4,
                        "unit": "unidad",
                    },
                ],
                "consent": True,
            }
        )

        self.assertEqual(errors, [])
        self.assertEqual(quote["product_category"], "varios")
        self.assertEqual(quote["quantity"], 34)

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
