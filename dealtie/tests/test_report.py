import unittest

from dealtie.report import build_html_report


class ReportTests(unittest.TestCase):
    def test_report_contains_finding_and_source_trace(self):
        html = build_html_report([{
            "metric": "Adjusted EBITDA",
            "period": "FY2025",
            "status": "VALUE_MISMATCH",
            "explanation": "Observed spread: 0.8 USD m.",
            "observations": [{
                "document": "QoE final",
                "value": "20.8",
                "unit": "USD m",
                "source_ref": "PDF p.26",
            }],
        }], tolerance="0.01", generated_at="2026-11-04T12:00:00Z")
        self.assertIn("Adjusted EBITDA", html)
        self.assertIn("VALUE MISMATCH", html)
        self.assertIn("QoE final", html)
        self.assertIn("PDF p.26", html)
        self.assertIn("0.01", html)

    def test_report_escapes_user_supplied_text(self):
        html = build_html_report([{
            "metric": "<script>alert(1)</script>",
            "period": "FY2025",
            "status": "TIED",
            "explanation": "<img src=x onerror=alert(1)>",
            "observations": [{
                "document": "<b>hostile</b>",
                "value": "1",
                "unit": "USD m",
                "source_ref": "<svg onload=alert(1)>",
            }],
        }], generated_at="test")
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertNotIn("<svg onload", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;svg onload=alert(1)&gt;", html)

    def test_empty_report_is_still_readable(self):
        html = build_html_report([], generated_at="test")
        self.assertIn("No findings were generated.", html)
        self.assertIn("No comparable observations were supplied.", html)
        self.assertIn("Review boundary.", html)


if __name__ == "__main__":
    unittest.main()
