import unittest

from backend.ghl_logic import build_crm_sync_record
from backend.lead_logic import build_lead_record
from backend.quote_logic import build_quote_record


class GoHighLevelLogicTest(unittest.TestCase):
    def build_lead(self):
        quote, errors = build_quote_record(
            {
                "full_name": "Carlos Ramirez",
                "email": "carlos@example.com",
                "phone": "+57 301 222 3344",
                "customer_type": "empresa",
                "company_name": "Obra Electrica Norte",
                "request_type": "quote",
                "product_category": "tuberia",
                "quantity": "80",
                "unit": "unidad",
                "budget": "1800000",
                "urgency": "hoy",
                "delivery_city": "Los Patios",
                "items": [
                    {
                        "sku": "TUB-PVC-12",
                        "name": "Tuberia PVC 1/2 pulgada",
                        "category": "tuberia",
                        "quantity": 80,
                        "unit": "unidad",
                    }
                ],
                "consent": True,
            }
        )
        self.assertEqual(errors, [])
        lead, lead_errors = build_lead_record({"quote": quote})
        self.assertEqual(lead_errors, [])
        return lead

    def test_safe_mode_builds_contact_and_opportunity_without_sending(self):
        lead = self.build_lead()
        sync, errors = build_crm_sync_record({"lead": lead}, env={"GHL_ENABLED": "false"})

        self.assertEqual(errors, [])
        self.assertEqual(sync["mode"], "safe_mode")
        self.assertEqual(sync["status"], "dry_run_prepared")
        self.assertFalse(sync["will_send_to_crm"])
        self.assertEqual(sync["requests"]["contact_upsert"]["url"], "https://services.leadconnectorhq.com/contacts/upsert")
        self.assertEqual(sync["requests"]["opportunity_create"]["body"]["pipelineStageId"], "<GHL_STAGE_HIGH>")
        self.assertIn("GHL_PRIVATE_TOKEN", sync["missing_config"])
        self.assertIn("contacts/upsert", sync["duplicate_strategy"])

    def test_live_check_reports_ready_when_config_exists(self):
        lead = self.build_lead()
        sync, errors = build_crm_sync_record(
            {"lead": lead},
            env={
                "GHL_ENABLED": "true",
                "GHL_PRIVATE_TOKEN": "token_123456789",
                "GHL_LOCATION_ID": "loc_123",
                "GHL_PIPELINE_ID": "pipe_123",
                "GHL_STAGE_HIGH": "stage_high",
            },
        )

        self.assertEqual(errors, [])
        self.assertEqual(sync["mode"], "live_check")
        self.assertEqual(sync["status"], "ready_for_live_sync")
        self.assertFalse(sync["will_send_to_crm"])
        self.assertEqual(sync["missing_config"], [])
        self.assertEqual(sync["requests"]["contact_upsert"]["body"]["locationId"], "loc_123")
        self.assertEqual(sync["requests"]["opportunity_create"]["body"]["pipelineStageId"], "stage_high")
        self.assertEqual(sync["requests"]["contact_upsert"]["headers"]["Authorization"], "Bearer ***6789")

    def test_missing_lead_returns_errors(self):
        sync, errors = build_crm_sync_record({"lead": {"email": ""}}, env={})

        self.assertIn("lead_id_required", errors)
        self.assertIn("quote_id_required", errors)
        self.assertIn("full_name_required", errors)
        self.assertIn("email_or_phone_required", errors)
        self.assertEqual(sync["lead"].get("email"), "")


if __name__ == "__main__":
    unittest.main()
