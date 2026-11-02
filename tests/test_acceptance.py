import unittest

from validator.acceptance import compare_runs, evaluate_run


def protocol():
    return {
        "protocol_id": "SUPPORT-ROUTING",
        "version": "1.0",
        "case_set_version": "1.0",
        "workflow": "Support ticket routing",
        "criteria": [
            {
                "criterion_id": "route-correct",
                "type": "exact_match",
                "field": "route",
                "severity": "critical",
                "minimum_pass_rate": 1.0
            },
            {
                "criterion_id": "response-present",
                "type": "required_field",
                "field": "response",
                "severity": "major",
                "minimum_pass_rate": 1.0
            },
            {
                "criterion_id": "tone-review",
                "type": "human_review",
                "severity": "minor",
                "minimum_pass_rate": 1.0
            }
        ],
        "decision_rules": {
            "minimum_overall_pass_rate": 1.0,
            "minimum_case_coverage": 1.0,
            "hard_fail_severities": ["critical"]
        }
    }


def cases():
    return [
        {
            "case_id": "C-001",
            "criterion_ids": "route-correct;response-present;tone-review",
            "expected_json": {"route": "billing"}
        },
        {
            "case_id": "C-002",
            "criterion_ids": "route-correct;response-present;tone-review",
            "expected_json": {"route": "technical"}
        }
    ]


def run(route2="technical"):
    return [
        {"case_id": "C-001", "output_json": {"route": "billing", "response": "We can help."}},
        {"case_id": "C-002", "output_json": {"route": route2, "response": "Please provide details."}}
    ]


def reviews(decision="PASS"):
    return [
        {"case_id": "C-001", "criterion_id": "tone-review", "decision": decision, "rationale": "Reviewed."},
        {"case_id": "C-002", "criterion_id": "tone-review", "decision": decision, "rationale": "Reviewed."}
    ]


class AcceptanceTests(unittest.TestCase):
    def test_complete_passing_run(self):
        result = evaluate_run(protocol(), cases(), run(), reviews())
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["summary"]["case_coverage"], 1.0)

    def test_critical_failure_fails_acceptance(self):
        result = evaluate_run(protocol(), cases(), run("billing"), reviews())
        self.assertEqual(result["decision"], "FAIL")
        self.assertEqual(result["summary"]["hard_failure_count"], 1)

    def test_missing_case_is_insufficient_evidence(self):
        result = evaluate_run(protocol(), cases(), run()[:1], reviews()[:1])
        self.assertEqual(result["decision"], "INSUFFICIENT EVIDENCE")
        self.assertEqual(result["summary"]["case_coverage"], 0.5)

    def test_missing_human_review_is_insufficient(self):
        result = evaluate_run(protocol(), cases(), run())
        self.assertEqual(result["decision"], "INSUFFICIENT EVIDENCE")

    def test_regression_is_identified(self):
        baseline = evaluate_run(protocol(), cases(), run(), reviews())
        candidate = evaluate_run(protocol(), cases(), run("billing"), reviews())
        comparison = compare_runs(baseline, candidate)
        self.assertEqual(comparison["regression_count"], 1)
        self.assertEqual(comparison["candidate_decision"], "FAIL")

    def test_duplicate_case_ids_are_rejected(self):
        duplicated = cases() + [cases()[0]]
        with self.assertRaisesRegex(ValueError, "Duplicate test case ID"):
            evaluate_run(protocol(), duplicated, run(), reviews())

    def test_invalid_review_decision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid review decision"):
            evaluate_run(protocol(), cases(), run(), [
                {"case_id": "C-001", "criterion_id": "tone-review", "decision": "MAYBE"}
            ])


if __name__ == "__main__":
    unittest.main()
