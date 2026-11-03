import unittest
from decimal import Decimal
from dealtie.reconcile import reconcile


class ReconcileTests(unittest.TestCase):
    def row(self, doc, value, unit="USD m", source_ref="p.1", metric="Revenue", period="FY2025"):
        return {"document": doc, "metric": metric, "period": period, "value": value,
                "unit": unit, "source_ref": source_ref}

    def test_tied(self):
        result = reconcile([self.row("CIM", "100"), self.row("QoE", "100.00")])
        self.assertEqual(result[0]["status"], "TIED")

    def test_value_mismatch(self):
        result = reconcile([self.row("CIM", "100"), self.row("QoE", "98")])
        self.assertEqual(result[0]["status"], "VALUE_MISMATCH")

    def test_unit_mismatch(self):
        result = reconcile([self.row("CIM", "100"), self.row("Model", "100", "EUR m")])
        self.assertEqual(result[0]["status"], "UNIT_MISMATCH")

    def test_missing_value(self):
        result = reconcile([self.row("CIM", ""), self.row("QoE", "100")])
        self.assertEqual(result[0]["status"], "MISSING_OR_NON_NUMERIC")

    def test_single_source(self):
        result = reconcile([self.row("CIM", "100")])
        self.assertEqual(result[0]["status"], "INSUFFICIENT_COVERAGE")

    def test_missing_unit_is_not_tied(self):
        result = reconcile([self.row("CIM", "100", ""), self.row("QoE", "100")])
        self.assertEqual(result[0]["status"], "MISSING_OR_NON_NUMERIC")

    def test_missing_source_reference_is_not_tied(self):
        result = reconcile([self.row("CIM", "100", source_ref=""), self.row("QoE", "100")])
        self.assertEqual(result[0]["status"], "MISSING_OR_NON_NUMERIC")

    def test_parentheses_are_negative(self):
        result = reconcile([self.row("CIM", "(100)"), self.row("QoE", "-100.00")])
        self.assertEqual(result[0]["status"], "TIED")

    def test_non_finite_values_are_rejected(self):
        result = reconcile([self.row("CIM", "NaN"), self.row("QoE", "100")])
        self.assertEqual(result[0]["status"], "MISSING_OR_NON_NUMERIC")

    def test_tolerance(self):
        result = reconcile([self.row("CIM", "100"), self.row("QoE", "100.01")], tolerance=Decimal("0.01"))
        self.assertEqual(result[0]["status"], "TIED")

    def test_invalid_tolerance(self):
        with self.assertRaises(ValueError):
            reconcile([], tolerance="-1")

    def test_normalizes_group_keys(self):
        result = reconcile([
            self.row("CIM", "100", metric=" Revenue ", period="FY2025"),
            self.row("QoE", "100", metric="revenue", period=" FY2025 ")
        ])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "TIED")

    def test_ignores_unmappable_rows(self):
        self.assertEqual(reconcile([{"document": "CIM", "value": "10"}]), [])

    def test_percentage_and_multiple_suffixes(self):
        self.assertEqual(reconcile([
            self.row("CIM", "38.2%", unit="%"),
            self.row("QoE", "38.20%", unit="%")
        ])[0]["status"], "TIED")
        self.assertEqual(reconcile([
            self.row("CIM", "4.2x", unit="x"),
            self.row("QoE", "4.20x", unit="x")
        ])[0]["status"], "TIED")

    def test_duplicate_source_reference_is_flagged(self):
        result = reconcile([
            self.row("CIM", "100", source_ref="p.1"),
            self.row("CIM", "100", source_ref="p.1"),
            self.row("QoE", "100", source_ref="p.3")
        ])
        self.assertEqual(result[0]["status"], "DUPLICATE_SOURCE_ENTRY")

    def test_same_metric_different_periods_are_separate(self):
        result = reconcile([
            self.row("CIM", "100", period="FY2024"),
            self.row("QoE", "100", period="FY2024"),
            self.row("CIM", "110", period="FY2025"),
            self.row("QoE", "110", period="FY2025")
        ])
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
