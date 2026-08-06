import unittest

from backend.lead_logic import build_lead_record, build_notification
from backend.quote_logic import build_quote_record


class LeadLogicTest(unittest.TestCase):
    def test_build_high_priority_lead_from_quote_response(self):
        quote, errors = build_quote_record(
            {
                "full_name": "Ana Perez",
                "email": "ana@example.com",
                "phone": "+57 300 123 4567",
                "customer_type": "empresa",
                "company_name": "Obra Norte",
                "request_type": "quote",
                "product_category": "cable",
                "quantity": "150",
                "unit": "metro",
                "budget": "$2.500.000",
                "urgency": "hoy",
                "delivery_city": "Los Patios",
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
        lead, lead_errors = build_lead_record({"quote": quote, "duplicate": False})

        self.assertEqual(lead_errors, [])
        self.assertEqual(lead["quote_id"], quote["id"])
        self.assertEqual(lead["priority"], "high")
        self.assertEqual(lead["pipeline_stage"], "contactar_hoy")
        self.assertIn("prioridad_high", lead["tags"])
        self.assertIn("categoria_cable", lead["tags"])
        self.assertEqual(lead["sheet_row"]["telefono"], "+573001234567")
        self.assertEqual(lead["ghl_payloads"]["contact"]["firstName"], "Ana")
        self.assertIn("Nuevo lead high", lead["advisor_message"])

    def test_missing_quote_data_returns_errors(self):
        lead, errors = build_lead_record({"quote": {"email": ""}})

        self.assertIn("quote_id_required", errors)
        self.assertIn("full_name_required", errors)
        self.assertIn("phone_required", errors)
        self.assertEqual(lead["quote"].get("email"), "")

    def test_notification_keeps_lead_reference(self):
        notification = build_notification(
            {
                "lead": {
                    "id": "lead-1",
                    "quote_id": "quote-1",
                    "priority": "high",
                    "advisor_message": "Llamar a cliente prioritario",
                }
            }
        )

        self.assertEqual(notification["lead_id"], "lead-1")
        self.assertEqual(notification["quote_id"], "quote-1")
        self.assertEqual(notification["priority"], "high")
        self.assertEqual(notification["status"], "prepared")


if __name__ == "__main__":
    unittest.main()
