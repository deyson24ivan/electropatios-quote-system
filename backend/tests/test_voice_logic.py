import unittest

from backend.voice_logic import build_voice_call_record


class VoiceLogicTest(unittest.TestCase):
    def test_quote_call_gets_safe_reply_and_handoff(self):
        call, errors = build_voice_call_record(
            {
                "caller_name": "Carlos Ramirez",
                "phone": "+57 301 222 3344",
                "delivery_city": "Los Patios",
                "transcript": "Necesito 120 metros de cable THHN para hoy.",
            }
        )

        self.assertEqual(errors, [])
        self.assertEqual(call["mode"], "safe_mode")
        self.assertFalse(call["will_call_voice_provider"])
        self.assertFalse(call["will_call_ai_model"])
        self.assertEqual(call["intent"], "quote")
        self.assertEqual(call["product_category"], "cable")
        self.assertEqual(call["quantity"], 120)
        self.assertEqual(call["priority"], "high")
        self.assertTrue(call["handoff_required"])
        self.assertIn("confirma precio", call["safe_voice_reply"])
        self.assertEqual(call["voice_lead_draft"]["source"], "voice_ai_safe_mode")

    def test_technical_call_does_not_give_installation_advice(self):
        call, errors = build_voice_call_record(
            {
                "caller_name": "Luis Mora",
                "phone": "3001234567",
                "transcript": "Que breaker debo instalar para una carga de 40 amperios?",
            }
        )

        self.assertEqual(errors, [])
        self.assertEqual(call["intent"], "technical_advice")
        self.assertEqual(call["priority"], "high")
        self.assertTrue(call["handoff_required"])
        self.assertEqual(call["handoff_reason"], "consulta_tecnica")
        self.assertIn("asesor revisa los datos", call["safe_voice_reply"])

    def test_empty_call_requires_transcript(self):
        call, errors = build_voice_call_record({})

        self.assertIn("transcript_required", errors)
        self.assertEqual(call["intent"], "unknown")
        self.assertTrue(call["handoff_required"])
        self.assertEqual(call["confidence"], "low")


if __name__ == "__main__":
    unittest.main()
