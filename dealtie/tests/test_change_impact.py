import unittest
from dealtie.change_impact import analyze_version_impact


class ChangeImpactTests(unittest.TestCase):
    def row(self, family, version, document, value, source_ref, metric="Adjusted EBITDA", period="FY2025", unit="USD m"):
        return {
            "document_family": family, "version": version, "document": document,
            "metric": metric, "period": period, "value": value,
            "unit": unit, "source_ref": source_ref,
        }

    def test_detects_change_and_stale_downstream_reference(self):
        rows = [
            self.row("QoE", "v1", "QoE v1", "18.2", "p.12"),
            self.row("QoE", "v2", "QoE v2", "17.6", "p.13"),
            self.row("CIM", "v1", "CIM v1", "18.2", "p.21"),
            self.row("Valuation model", "v3", "Model v3", "17.6", "Summary!D8"),
        ]
        result = analyze_version_impact(rows, "v1", "v2")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["change"], "-0.6")
        states = {item["document_family"]: item["state"] for item in result[0]["downstream_references"]}
        self.assertEqual(states["CIM"], "STALE_CANDIDATE")
        self.assertEqual(states["Valuation model"], "ALIGNED_TO_CURRENT")
        self.assertTrue(result[0]["review_required"])

    def test_does_not_infer_unit_conversion(self):
        rows = [
            self.row("QoE", "v1", "QoE v1", "18.2", "p.12"),
            self.row("QoE", "v2", "QoE v2", "17.6", "p.13"),
            self.row("CIM", "v1", "CIM v1", "17.6", "p.21", unit="USD thousands"),
        ]
        result = analyze_version_impact(rows, "v1", "v2")
        self.assertEqual(result[0]["downstream_references"][0]["state"], "INSUFFICIENT_EVIDENCE")

    def test_no_change_returns_empty(self):
        rows = [
            self.row("QoE", "v1", "QoE v1", "18.2", "p.12"),
            self.row("QoE", "v2", "QoE v2", "18.2", "p.13"),
        ]
        self.assertEqual(analyze_version_impact(rows, "v1", "v2"), [])

    def test_requires_distinct_versions(self):
        with self.assertRaises(ValueError):
            analyze_version_impact([], "v1", "v1")

    def test_invalid_tolerance(self):
        with self.assertRaises(ValueError):
            analyze_version_impact([], "v1", "v2", "-0.1")


if __name__ == "__main__":
    unittest.main()
