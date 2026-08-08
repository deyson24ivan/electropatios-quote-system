import unittest

from backend.tracking_logic import build_tracking_event


class TrackingLogicTest(unittest.TestCase):
    def test_valid_tracking_event_cleans_utm_data(self):
        event, errors = build_tracking_event(
            {
                "event_name": "product_add",
                "session_id": "session-123",
                "page_path": "/?utm_source=Facebook&utm_campaign=Cables Agosto",
                "page_title": "Electropatios",
                "utm_source": "Facebook",
                "utm_medium": "Paid Social",
                "utm_campaign": "Cables Agosto",
                "metadata": {
                    "sku": "CAB-THHN-12",
                    "quantity": 2,
                    "nested": {"ignored": True},
                },
            }
        )

        self.assertEqual(errors, [])
        self.assertEqual(event["mode"], "local_tracking")
        self.assertEqual(event["event_name"], "product_add")
        self.assertEqual(event["utm_source"], "facebook")
        self.assertEqual(event["utm_medium"], "paid_social")
        self.assertEqual(event["utm_campaign"], "cables_agosto")
        self.assertEqual(event["metadata"]["sku"], "CAB-THHN-12")
        self.assertEqual(event["metadata"]["quantity"], 2)
        self.assertIn("ignored", event["metadata"]["nested"])

    def test_missing_event_name_returns_error(self):
        event, errors = build_tracking_event({})

        self.assertIn("event_name_required", errors)
        self.assertEqual(event["event_name"], "unknown")

    def test_unknown_event_name_returns_error(self):
        event, errors = build_tracking_event({"event_name": "random_click"})

        self.assertIn("event_name_not_allowed", errors)
        self.assertEqual(event["event_name"], "random_click")


if __name__ == "__main__":
    unittest.main()
