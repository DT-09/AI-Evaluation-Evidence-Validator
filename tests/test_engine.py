import unittest
import pandas as pd

from validator.engine import calculate_metrics, validate_dataframe


class MetricTests(unittest.TestCase):
    def test_confusion_matrix_and_metrics(self):
        pairs = [(1, 1), (1, 0), (0, 1), (0, 0), (0, 0), (1, 1)]
        result = calculate_metrics(pairs)
        self.assertEqual(result["confusion_matrix"], {"tp": 2, "fp": 1, "tn": 2, "fn": 1})
        self.assertAlmostEqual(result["metrics"]["accuracy"], 4 / 6)
        self.assertAlmostEqual(result["metrics"]["precision"], 2 / 3)
        self.assertAlmostEqual(result["metrics"]["recall"], 2 / 3)
        self.assertAlmostEqual(result["metrics"]["f1"], 2 / 3)
        self.assertAlmostEqual(result["metrics"]["specificity"], 2 / 3)

    def test_claim_mismatch_is_flagged(self):
        frame = pd.DataFrame([
            {"record_id":"a","split":"test","actual":"1","predicted":"1"},
            {"record_id":"b","split":"test","actual":"0","predicted":"0"},
        ])
        result = validate_dataframe(frame, {"metrics":{"accuracy":0.25}}, tolerance=0.001)
        flags = {c["check_id"] for c in result["checks"] if c["status"] == "FLAG"}
        self.assertIn("claim.accuracy", flags)

    def test_duplicate_and_cross_split_ids(self):
        frame = pd.DataFrame([
            {"record_id":"same","split":"train","actual":"1","predicted":"1"},
            {"record_id":"same","split":"test","actual":"0","predicted":"0"},
        ])
        result = validate_dataframe(frame)
        statuses = {c["check_id"]: c["status"] for c in result["checks"]}
        self.assertEqual(statuses["data.duplicate_record_ids"], "FLAG")
        self.assertEqual(statuses["data.cross_split_id_overlap"], "FLAG")

    def test_invalid_label_excluded_and_flagged(self):
        frame = pd.DataFrame([
            {"record_id":"a","split":"test","actual":"yes","predicted":"1"},
            {"record_id":"b","split":"test","actual":"0","predicted":"0"},
        ])
        result = validate_dataframe(frame)
        statuses = {c["check_id"]: c["status"] for c in result["checks"]}
        self.assertEqual(statuses["data.binary_labels"], "FLAG")
        self.assertEqual(result["recalculated"]["sample_count"], 1)

    def test_missing_schema_stops_metric_calculation(self):
        frame = pd.DataFrame([{"actual":"1","predicted":"1"}])
        result = validate_dataframe(frame)
        self.assertEqual(result["recalculated"]["sample_count"], 0)
        self.assertEqual(result["checks"][0]["status"], "FLAG")


if __name__ == "__main__":
    unittest.main()
