"""Regression coverage for grouped Alertmanager alerts."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "incident-triage/scripts"))
import normalize_alert  # noqa: E402


class AlertNormalizationTests(unittest.TestCase):
    def test_group_preserves_each_alert_without_assigning_first_target_to_group(self):
        payload = {
            "status": "firing",
            "groupLabels": {"alertname": "WorkloadHealth"},
            "commonLabels": {"service": "checkout", "environment": "prod", "region": "eu-west-1", "team": "payments"},
            "commonAnnotations": {"dashboard_url": "https://grafana.example/d/checkout"},
            "alerts": [
                {
                    "labels": {"severity": "critical", "cluster": "cluster-a", "namespace": "payments", "pod": "pay-1"},
                    "annotations": {"summary": "Payments unavailable", "diagnostic_hint": "synthetic-detail"},
                },
                {
                    "labels": {"severity": "warning", "cluster": "cluster-b", "namespace": "orders", "pod": "order-2"},
                    "annotations": {"summary": "Orders delayed"},
                },
            ],
        }

        result = normalize_alert.normalize(payload)

        self.assertEqual(result["alert_count"], 2)
        self.assertEqual(len(result["alerts"]), 2)
        self.assertEqual([alert["severity"] for alert in result["alerts"]], ["critical", "warning"])
        self.assertEqual([alert["namespace"] for alert in result["alerts"]], ["payments", "orders"])
        self.assertEqual([alert["cluster"] for alert in result["alerts"]], ["cluster-a", "cluster-b"])
        self.assertEqual(result["service"], "checkout")
        self.assertEqual(result["environment"], "prod")
        self.assertEqual(result["severity"], "")
        self.assertEqual(result["namespace"], "")
        self.assertEqual(result["cluster"], "")
        self.assertEqual(result["summary"], "")
        self.assertEqual(result["alerts"][0]["annotations"]["diagnostic_hint"], "synthetic-detail")
        self.assertEqual(result["labels"]["region"], "eu-west-1")
        self.assertEqual(result["alerts"][1]["labels"]["team"], "payments")

    def test_single_alert_keeps_legacy_top_level_fields_and_adds_member(self):
        result = normalize_alert.normalize({
            "alerts": [{
                "labels": {"alertname": "HighLatency", "severity": "page", "namespace": "api"},
                "annotations": {"summary": "Latency high"},
            }],
        })

        self.assertEqual(result["alert_count"], 1)
        self.assertEqual(result["severity"], "page")
        self.assertEqual(result["namespace"], "api")
        self.assertEqual(result["summary"], "Latency high")
        self.assertEqual(len(result["alerts"]), 1)


if __name__ == "__main__":
    unittest.main()
