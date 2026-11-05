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
        for invalid in ("-1", "NaN", "Infinity", "not-a-number"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    reconcile([], tolerance=invalid)

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

    def test_valid_thousands_grouping(self):
        result = reconcile([self.row("CIM", "1,200.5"), self.row("QoE", "1,200.50")])
        self.assertEqual(result[0]["status"], "TIED")

    def test_malformed_thousands_grouping_is_rejected(self):
        result = reconcile([self.row("CIM", "1,2"), self.row("QoE", "12")])
        self.assertEqual(result[0]["status"], "MISSING_OR_NON_NUMERIC")

    def test_currency_symbol_in_value_is_not_silently_stripped(self):
        result = reconcile([self.row("CIM", "$100"), self.row("QoE", "100")])
        self.assertEqual(result[0]["status"], "MISSING_OR_NON_NUMERIC")

    def test_duplicate_source_reference_is_flagged(self):
        result = reconcile([
            self.row("CIM", "100", source_ref="p.1"),
            self.row("CIM", "100", source_ref="p.1"),
            self.row("QoE", "100", source_ref="p.3")
        ])
        self.assertEqual(result[0]["status"], "DUPLICATE_SOURCE_ENTRY")

    def test_findings_are_ordered_by_review_priority(self):
        rows = [
            self.row("CIM", "100", metric="F Tied"),
            self.row("QoE", "100", metric="F Tied"),
            self.row("CIM", "100", metric="A Value"),
            self.row("QoE", "90", metric="A Value"),
            self.row("CIM", "100", metric="B Unit"),
            self.row("Model", "100", unit="EUR m", metric="B Unit"),
            self.row("CIM", "100", metric="C Duplicate", source_ref="p.1"),
            self.row("CIM", "100", metric="C Duplicate", source_ref="p.1"),
            self.row("QoE", "100", metric="C Duplicate", source_ref="p.2"),
            self.row("CIM", "", metric="D Missing"),
            self.row("QoE", "100", metric="D Missing"),
            self.row("CIM", "100", metric="E Coverage"),
        ]
        findings = reconcile(rows)
        self.assertEqual(
            [item["status"] for item in findings],
            [
                "VALUE_MISMATCH",
                "UNIT_MISMATCH",
                "DUPLICATE_SOURCE_ENTRY",
                "MISSING_OR_NON_NUMERIC",
                "INSUFFICIENT_COVERAGE",
                "TIED",
            ],
        )
        self.assertEqual([item["review_priority"] for item in findings], [1, 1, 2, 2, 3, 4])
        self.assertEqual(findings[0]["review_priority_label"], "Resolve comparison")

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
