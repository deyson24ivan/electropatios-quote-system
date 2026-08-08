import unittest

from backend.email_logic import build_email_dns_plan


class EmailLogicTest(unittest.TestCase):
    def test_valid_domain_builds_safe_dns_plan(self):
        plan, errors = build_email_dns_plan(
            {
                "domain": "electropatios.com",
                "providers": ["google_workspace", "gohighlevel"],
                "report_email": "dmarc@electropatios.com",
            }
        )

        self.assertEqual(errors, [])
        self.assertEqual(plan["mode"], "safe_mode")
        self.assertFalse(plan["will_change_dns"])
        self.assertEqual(plan["domain"], "electropatios.com")
        self.assertEqual(plan["checks"]["dmarc_policy"], "none")
        self.assertEqual(plan["checks"]["spf_record_count_expected"], 1)

        purposes = {record["purpose"] for record in plan["records"]}
        self.assertIn("spf", purposes)
        self.assertIn("dkim", purposes)
        self.assertIn("dmarc", purposes)

    def test_invalid_domain_is_rejected(self):
        plan, errors = build_email_dns_plan({"domain": "https://electropatios.com"})

        self.assertIn("valid_domain_required", errors)
        self.assertEqual(plan["domain"], "https://electropatios.com")

    def test_unknown_provider_requires_manual_review(self):
        plan, errors = build_email_dns_plan(
            {
                "domain": "electropatios.com",
                "providers": ["proveedor_nuevo"],
            }
        )

        self.assertEqual(errors, [])
        self.assertEqual(plan["records"][0]["status"], "provider_required")
        self.assertTrue(any("Proveedor Nuevo" in warning for warning in plan["warnings"]))

    def test_bulk_volume_marks_unsubscribe_requirement(self):
        plan, errors = build_email_dns_plan(
            {
                "domain": "electropatios.com",
                "daily_volume": 5000,
            }
        )

        self.assertEqual(errors, [])
        self.assertTrue(plan["checks"]["bulk_sender"])
        self.assertTrue(plan["checks"]["one_click_unsubscribe_required"])


if __name__ == "__main__":
    unittest.main()
