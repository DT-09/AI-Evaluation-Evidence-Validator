"""Readable, self-contained HTML review report for DealTie findings."""
from datetime import datetime, timezone
from html import escape


_STATUS_LABELS = {
    "TIED": "Tied",
    "VALUE_MISMATCH": "Value mismatch",
    "UNIT_MISMATCH": "Unit mismatch",
    "MISSING_OR_NON_NUMERIC": "Missing / non-numeric",
    "DUPLICATE_SOURCE_ENTRY": "Duplicate source entry",
    "INSUFFICIENT_COVERAGE": "Insufficient coverage",
}


def build_html_report(findings, tolerance="0.01", generated_at=None):
    """Render findings and source observations into a standalone HTML report.

    The report is an evidence handoff, not a financial opinion. All supplied
    text is HTML-escaped because document labels and source references are
    user-controlled inputs.
    """
    timestamp = generated_at or datetime.now(timezone.utc).isoformat()
    safe_time = escape(str(timestamp))
    safe_tolerance = escape(str(tolerance))
    counts = {}
    for finding in findings:
        status = finding.get("status", "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1

    summary = "".join(
        f"<div class='stat'><strong>{count}</strong><span>{escape(_STATUS_LABELS.get(status, status))}</span></div>"
        for status, count in sorted(counts.items())
    ) or "<p>No findings were generated.</p>"

    sections = []
    for index, finding in enumerate(findings, start=1):
        status = str(finding.get("status", "UNKNOWN"))
        label = _STATUS_LABELS.get(status, status)
        metric = escape(str(finding.get("metric", "Unlabelled metric")))
        period = escape(str(finding.get("period", "Unspecified period")))
        explanation = escape(str(finding.get("explanation", "")))
        priority = int(finding.get("review_priority", 4))
        priority_label = escape(str(finding.get("review_priority_label", "No priority assigned")))
        observations = []
        for row in finding.get("observations", []):
            observations.append(
                "<tr>"
                f"<td>{escape(str(row.get('document', '')))}</td>"
                f"<td>{escape(str(row.get('value', '') if row.get('value') is not None else ''))}</td>"
                f"<td>{escape(str(row.get('unit', '')))}</td>"
                f"<td>{escape(str(row.get('source_ref', '')))}</td>"
                "</tr>"
            )
        table = (
            "<table><thead><tr><th>Source document</th><th>Reported value</th>"
            "<th>Unit</th><th>Source reference</th></tr></thead><tbody>"
            + "".join(observations)
            + "</tbody></table>"
        )
        sections.append(
            f"<article class='finding'><div class='finding-head'><span class='number'>"
            f"{index:02d}</span><div><h2>{metric}</h2><p class='period'>{period}</p></div>"
            f"<span class='priority'>P{priority} · {priority_label}</span>"
            f"<span class='status'>{escape(label)}</span></div><p>{explanation}</p>{table}</article>"
        )

    body = "".join(sections) or "<p>No comparable observations were supplied.</p>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DealTie — Financial Evidence Review</title>
<style>
:root{{--ink:#20221f;--muted:#686b63;--paper:#f4f1e9;--panel:#fffefa;--line:#d9d5ca;--accent:#496b5d;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:14px/1.55 Arial,sans-serif}}
main{{max-width:1080px;margin:0 auto;padding:48px 28px 72px}}header{{border-bottom:2px solid var(--ink);padding-bottom:26px}}
.brand{{font:700 12px/1 monospace;letter-spacing:.2em;color:var(--accent)}}h1{{font:normal 42px/1.08 Georgia,serif;margin:22px 0 8px}}
.meta{{color:var(--muted);font:12px monospace}}.notice{{margin:24px 0;padding:14px 17px;border-left:3px solid var(--accent);background:#e8e9e1;color:#42483f}}
.summary{{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0 34px}}.stat{{min-width:130px;padding:14px 16px;background:var(--panel);border:1px solid var(--line)}}
.stat strong{{display:block;font:28px Georgia,serif}}.stat span{{font-size:11px;color:var(--muted)}}
.finding{{margin:18px 0;padding:22px;background:var(--panel);border:1px solid var(--line);break-inside:avoid}}
.finding-head{{display:flex;align-items:center;gap:14px}}.number{{font:italic 18px Georgia,serif;color:var(--accent)}}
h2{{font:normal 24px Georgia,serif;margin:0}}.period{{font:11px monospace;color:var(--muted);margin:3px 0 0}}
.priority{{padding:5px 9px;background:#ece9df;color:#57594f;font:10px monospace}}.status{{margin-left:auto;padding:5px 9px;border:1px solid var(--line);font:10px monospace;text-transform:uppercase}}
table{{width:100%;border-collapse:collapse;margin-top:18px;font-size:12px}}th{{text-align:left;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.08em}}
th,td{{padding:10px 8px;border-bottom:1px solid var(--line);vertical-align:top}}footer{{margin-top:34px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:11px}}
@media(max-width:640px){{main{{padding:28px 16px}}h1{{font-size:34px}}.finding-head{{align-items:flex-start;flex-wrap:wrap}}.status{{margin-left:0}}.priority{{margin-left:0}}table{{font-size:11px}}}}
@media print{{body{{background:white}}main{{padding:0;max-width:none}}.finding{{break-inside:avoid}}}}
</style></head><body><main>
<header><div class="brand">DEALTIE / FINANCIAL EVIDENCE RECONCILIATION</div>
<h1>Financial evidence review</h1>
<div class="meta">Generated {safe_time} · Comparison tolerance: {safe_tolerance}</div></header>
<div class="notice"><strong>Review boundary.</strong> A mismatch is an investigation lead, not proof of an error, misstatement, financial loss or recoverable amount. Review priority is a workflow order, not a financial materiality or risk score. This report is not an audit opinion, QoE conclusion, valuation opinion, legal opinion or transaction recommendation.</div>
<section class="summary">{summary}</section>
{body}
<footer>DealTie records analyst-confirmed observations and applies explicit comparison rules. It does not determine which source is authoritative, convert currencies or periods, evaluate workbook formulas, or provide accounting judgement. A qualified finance professional must review substantive conclusions. Prototype output: use synthetic or properly authorised and redacted data only.</footer>
</main></body></html>"""
