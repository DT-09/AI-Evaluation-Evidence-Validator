from __future__ import annotations

import io
import json
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from validator.acceptance import (
    compare_runs, evaluate_run, render_html_report, sha256, validate_protocol
)

st.set_page_config(page_title="AI Acceptance Assurance", page_icon="◈", layout="wide")

PAPER = "#f4f2eb"
INK = "#202820"
MUTED = "#667067"
ACCENT = "#92744f"

st.markdown(f"""
<style>
:root {{ --paper:{PAPER}; --ink:{INK}; --muted:{MUTED}; --accent:{ACCENT}; }}
.stApp {{ background:var(--paper); color:var(--ink); }}
.block-container {{ max-width:1240px; padding-top:2.2rem; padding-bottom:4rem; }}
h1,h2,h3 {{ font-family:Georgia,serif !important; color:var(--ink); }}
p,div,label {{ font-family:Arial,sans-serif; }}
.eyebrow {{font:600 11px monospace;letter-spacing:.16em;color:var(--accent);text-transform:uppercase}}
.hero {{padding:1.3rem 0 1.8rem;border-bottom:1px solid #dedbd1;margin-bottom:1.6rem}}
.hero h1 {{font-size:2.7rem;line-height:1.08;margin:.6rem 0}}
.sub {{max-width:780px;color:var(--muted);font-size:1.02rem;line-height:1.6}}
div[data-testid="stMetric"] {{background:white;border:1px solid #dedbd1;padding:14px;border-radius:3px}}
.stButton>button,.stDownloadButton>button {{border-radius:2px;border:1px solid #343d35;background:#343d35;color:#fff;min-height:2.6rem}}
.stButton>button:hover,.stDownloadButton>button:hover {{background:#4c5b50;color:white;border-color:#4c5b50}}
div[data-testid="stFileUploader"] {{background:white;border:1px dashed #bcb9ad;padding:.8rem}}
footer {{visibility:hidden}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">Buyer-owned AI supplier acceptance</div>
  <h1>Accept against your criteria.<br>Keep the evidence.</h1>
  <p class="sub">Define a versioned acceptance protocol, evaluate supplier outputs against the same buyer-owned cases, review exceptions and compare system changes with an accepted baseline.</p>
</div>
""", unsafe_allow_html=True)

DEFAULT_PROTOCOL = {
    "protocol_id": "SUPPORT-ROUTING-001",
    "version": "1.0",
    "case_set_version": "1.0",
    "workflow": "Customer support ticket routing",
    "criteria": [
        {"criterion_id": "route-correct", "type": "exact_match", "field": "route", "severity": "critical", "minimum_pass_rate": 1.0},
        {"criterion_id": "response-present", "type": "required_field", "field": "response", "severity": "major", "minimum_pass_rate": 1.0},
        {"criterion_id": "tone-review", "type": "human_review", "severity": "minor", "minimum_pass_rate": 1.0}
    ],
    "decision_rules": {
        "minimum_overall_pass_rate": 1.0,
        "minimum_case_coverage": 1.0,
        "hard_fail_severities": ["critical"]
    }
}

def read_csv_upload(upload, label):
    if upload is None:
        return None, None
    payload = upload.getvalue()
    try:
        frame = pd.read_csv(io.BytesIO(payload), dtype="string", keep_default_na=False)
    except Exception as exc:
        raise ValueError(f"{label} could not be read as CSV: {exc}") from exc
    return frame.to_dict(orient="records"), payload

def parse_reviews(upload, label):
    rows, payload = read_csv_upload(upload, label)
    return rows or [], payload

with st.sidebar:
    st.markdown("### Acceptance protocol")
    protocol_text = st.text_area(
        "Edit buyer-owned protocol JSON",
        value=json.dumps(DEFAULT_PROTOCOL, indent=2),
        height=420
    )
    st.caption("Protocol versions must be changed deliberately. Prior reports preserve the version used for each decision.")

try:
    protocol = json.loads(protocol_text)
    if not isinstance(protocol, dict):
        raise ValueError("Protocol must be a JSON object.")
    protocol_errors = validate_protocol(protocol)
except Exception as exc:
    st.error(f"Protocol is invalid: {exc}")
    st.stop()

if protocol_errors:
    st.error("Protocol needs correction: " + " · ".join(protocol_errors))
    st.stop()

protocol_bytes = json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode("utf-8")
st.download_button(
    "Download acceptance protocol",
    json.dumps(protocol, indent=2).encode("utf-8"),
    file_name=f"{protocol.get('protocol_id','acceptance-protocol')}-v{protocol.get('version','1')}.json",
    mime="application/json"
)

st.markdown("### 01 — Buyer-owned test cases")
cases_file = st.file_uploader("Upload case set CSV", type=["csv"], key="cases")
st.caption("Required columns: case_id, expected_json, criterion_ids. Add input_text or other context columns as needed.")

st.markdown("### 02 — Candidate system run")
candidate_file = st.file_uploader("Upload candidate run CSV", type=["csv"], key="candidate")
st.caption("Required columns: case_id, output_json. Each output_json cell must contain a JSON object.")

st.markdown("#### Candidate system metadata")
st.caption("Enter the identifiers supplied by the vendor or test environment. Leave unknown fields blank; the workbench will not infer versions.")
candidate_vendor = st.text_input("Supplier / vendor", key="candidate_vendor")
candidate_system_name = st.text_input("System / product name", key="candidate_system_name")
candidate_system_version = st.text_input("System / workflow version", key="candidate_system_version")
candidate_model_version = st.text_input("Model version", key="candidate_model_version")
candidate_prompt_version = st.text_input("Prompt / configuration version", key="candidate_prompt_version")
candidate_run_id = st.text_input("Run ID", key="candidate_run_id")

candidate_reviews_file = st.file_uploader("Candidate human-review decisions (optional)", type=["csv"], key="candidate_reviews")
st.caption("Review columns: case_id, criterion_id, decision (PASS / FAIL / INCONCLUSIVE), rationale, reviewer_id.")

st.markdown("### 03 — Accepted baseline (optional)")
baseline_file = st.file_uploader("Upload previously accepted baseline run CSV", type=["csv"], key="baseline")
st.markdown("#### Baseline system metadata")
baseline_vendor = st.text_input("Baseline supplier / vendor", key="baseline_vendor")
baseline_system_name = st.text_input("Baseline system / product name", key="baseline_system_name")
baseline_system_version = st.text_input("Baseline system / workflow version", key="baseline_system_version")
baseline_model_version = st.text_input("Baseline model version", key="baseline_model_version")
baseline_prompt_version = st.text_input("Baseline prompt / configuration version", key="baseline_prompt_version")
baseline_run_id = st.text_input("Baseline run ID", key="baseline_run_id")
baseline_reviews_file = st.file_uploader("Baseline human-review decisions (optional)", type=["csv"], key="baseline_reviews")

if not cases_file or not candidate_file:
    st.info("Upload a buyer-owned case set and candidate run to evaluate acceptance. Synthetic example files are in the repository's examples folder.")
    st.markdown("#### What the workbench does")
    a,b,c = st.columns(3)
    a.markdown("**Buyer-owned rules**\n\nVersioned criteria, severity and thresholds.")
    b.markdown("**Evidence-based decision**\n\nPASS, FAIL or INSUFFICIENT EVIDENCE.")
    c.markdown("**Change control**\n\nNew failures and resolved cases versus a baseline.")
    st.stop()

try:
    cases, cases_payload = read_csv_upload(cases_file, "Case set")
    candidate_rows, candidate_payload = read_csv_upload(candidate_file, "Candidate run")
    candidate_reviews, candidate_reviews_payload = parse_reviews(candidate_reviews_file, "Candidate reviews")
    candidate = evaluate_run(
        protocol, cases, candidate_rows, candidate_reviews,
        metadata={
            "vendor": candidate_vendor.strip() or None,
            "system_name": candidate_system_name.strip() or candidate_file.name,
            "system_version": candidate_system_version.strip() or None,
            "model_version": candidate_model_version.strip() or None,
            "prompt_or_configuration_version": candidate_prompt_version.strip() or None,
            "run_id": candidate_run_id.strip() or None,
            "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "protocol_sha256": sha256(protocol_bytes),
            "case_set_sha256": sha256(cases_payload),
            "run_file_sha256": sha256(candidate_payload),
            "review_file_sha256": sha256(candidate_reviews_payload) if candidate_reviews_payload else None
        }
    )

    baseline = None
    comparison = None
    if baseline_file is not None:
        baseline_rows, baseline_payload = read_csv_upload(baseline_file, "Baseline run")
        baseline_reviews, baseline_reviews_payload = parse_reviews(baseline_reviews_file, "Baseline reviews")
        baseline = evaluate_run(
            protocol, cases, baseline_rows, baseline_reviews,
            metadata={
                "vendor": baseline_vendor.strip() or None,
                "system_name": baseline_system_name.strip() or baseline_file.name,
                "system_version": baseline_system_version.strip() or None,
                "model_version": baseline_model_version.strip() or None,
                "prompt_or_configuration_version": baseline_prompt_version.strip() or None,
                "run_id": baseline_run_id.strip() or None,
                "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "protocol_sha256": sha256(protocol_bytes),
                "case_set_sha256": sha256(cases_payload),
                "run_file_sha256": sha256(baseline_payload),
                "review_file_sha256": sha256(baseline_reviews_payload) if baseline_reviews_payload else None
            }
        )
        comparison = compare_runs(baseline, candidate)
except Exception as exc:
    st.error(f"Evaluation could not be completed: {exc}")
    st.stop()

st.markdown("---")
st.markdown("### Acceptance decision")
decision = candidate["decision"]
if decision == "PASS":
    st.success("PASS — the candidate met the supplied protocol and evidence-coverage rules.")
elif decision == "FAIL":
    st.error("FAIL — one or more acceptance rules were not met.")
else:
    st.warning("INSUFFICIENT EVIDENCE — required cases, reviews or coverage are missing.")

summary = candidate["summary"]
m1,m2,m3,m4 = st.columns(4)
m1.metric("Case coverage", f"{summary['case_coverage']:.1%}")
m2.metric("Overall pass rate", "N/A" if summary["overall_pass_rate"] is None else f"{summary['overall_pass_rate']:.1%}")
m3.metric("Critical failures", summary["hard_failure_count"])
m4.metric("Cases in protocol", summary["case_count"])

st.markdown("#### Criterion results")
st.dataframe(pd.DataFrame(candidate["criterion_summary"]), use_container_width=True, hide_index=True)
st.markdown("#### Case-level evidence")
st.dataframe(pd.DataFrame(candidate["case_results"]), use_container_width=True, hide_index=True)

if summary["extra_run_case_ids"]:
    st.warning("The run contains case IDs not present in the buyer's case set: " + ", ".join(summary["extra_run_case_ids"]))

if comparison is not None:
    st.markdown("---")
    st.markdown("### Change comparison")
    x,y,z = st.columns(3)
    x.metric("Baseline decision", comparison["baseline_decision"])
    y.metric("Candidate decision", comparison["candidate_decision"])
    z.metric("Regressions", comparison["regression_count"])
    if comparison["changes"]:
        st.dataframe(pd.DataFrame(comparison["changes"]), use_container_width=True, hide_index=True)
    else:
        st.success("No case-level status changes were detected.")

st.markdown("---")
st.markdown("### Evidence package")
st.caption("The report records the protocol, test cases, run metadata, source hashes, criterion outcomes, decision rules and limitations.")
json_payload = json.dumps({"candidate": candidate, "baseline": baseline, "comparison": comparison}, indent=2).encode("utf-8")
html_payload = render_html_report(candidate, comparison).encode("utf-8")
d1,d2 = st.columns(2)
with d1:
    st.download_button("Download JSON evidence", json_payload, file_name="ai-acceptance-evidence.json", mime="application/json", use_container_width=True)
with d2:
    st.download_button("Download HTML report", html_payload, file_name="ai-acceptance-evidence.html", mime="text/html", use_container_width=True)

with st.expander("Decision semantics and limitations"):
    st.write("PASS means only that the supplied run met the stated acceptance rules. FAIL means a stated rule was not met. INSUFFICIENT EVIDENCE means the required coverage or review evidence is incomplete.")
    for item in candidate["limitations"]:
        st.write("• " + item)

st.caption("AI Acceptance Assurance · Local-first evaluation workbench · Human approval required")
