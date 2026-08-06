import unittest

from backend.ai_logic import build_ai_analysis
from backend.lead_logic import build_lead_record
from backend.quote_logic import build_quote_record


class AiLogicTest(unittest.TestCase):
    def build_lead_payload(self, notes="Necesito precio de cable THHN para hoy"):
        quote, errors = build_quote_record(
            {
                "full_name": "Ana Perez",
                "email": "ana@example.com",
                "phone": "+57 300 123 4567",
                "customer_type": "empresa",
                "request_type": "quote",
                "product_category": "cable",
                "quantity": "120",
                "unit": "metro",
                "budget": "2200000",
                "urgency": "hoy",
                "delivery_city": "Los Patios",
                "notes": notes,
                "items": [
                    {
                        "sku": "CAB-THHN-12",
                        "name": "Cable THHN #12",
                        "category": "cable",
                        "quantity": "120",
                        "unit": "metro",
                    }
                ],
                "consent": True,
            }
        )
        self.assertEqual(errors, [])
        lead, lead_errors = build_lead_record({"quote": quote})
        self.assertEqual(lead_errors, [])
        return {"quote": quote, "lead": lead}

    def test_quote_lead_gets_safe_handoff(self):
        payload = self.build_lead_payload()
        analysis, errors = build_ai_analysis(payload)

        self.assertEqual(errors, [])
        self.assertEqual(analysis["mode"], "safe_mode")
        self.assertFalse(analysis["will_call_ai_model"])
        self.assertEqual(analysis["intent"], "quote")
        self.assertEqual(analysis["category"], "cable")
        self.assertEqual(analysis["confidence"], "high")
        self.assertTrue(analysis["handoff_required"])
        self.assertIn("no_confirmar_price", analysis["guardrails"])
        self.assertIn("human_handoff", analysis["suggested_tags"])

    def test_technical_question_uses_guardrail(self):
        analysis, errors = build_ai_analysis(
            {
                "message": "Que breaker debo instalar para una carga de 40 amperios?",
                "question": "instalacion electrica",
            }
        )

        self.assertEqual(errors, [])
        self.assertEqual(analysis["intent"], "technical_advice")
        self.assertTrue(analysis["handoff_required"])
        self.assertIn("pasar_a_asesor_tecnico", analysis["guardrails"])
        self.assertIn("asesor debe revisar", analysis["safe_reply"])

    def test_unknown_message_requires_message(self):
        analysis, errors = build_ai_analysis({})

        self.assertIn("message_required", errors)
        self.assertEqual(analysis["intent"], "unknown")
        self.assertEqual(analysis["confidence"], "low")
        self.assertTrue(analysis["handoff_required"])


if __name__ == "__main__":
    unittest.main()
