from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from validator.engine import load_reported_metrics, render_html_report, validate_dataframe

st.set_page_config(page_title="AI Evaluation Evidence Validator", page_icon="◈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap');
:root { --ink:#222a25; --muted:#68736b; --paper:#f4f2eb; --line:#dfded4; --gold:#a1845c; }
.stApp { background:var(--paper); color:var(--ink); }
.block-container { max-width:1180px; padding-top:2.2rem; padding-bottom:4rem; }
h1,h2,h3 { font-family:'Playfair Display',Georgia,serif !important; color:var(--ink); }
p,div,label { font-family:'DM Sans',sans-serif; }
.eyebrow {font:500 11px 'DM Mono',monospace;letter-spacing:.16em;color:var(--gold);text-transform:uppercase}
.hero {padding:1.3rem 0 1.8rem;border-bottom:1px solid var(--line);margin-bottom:1.6rem}
.hero h1 {font-size:2.8rem;line-height:1.1;margin:.6rem 0}
.sub {max-width:720px;color:var(--muted);font-size:1.04rem}
.panel {background:#fff;border:1px solid var(--line);padding:1.1rem 1.3rem;border-radius:3px}
.metric {font:500 1.6rem 'DM Mono',monospace;color:var(--ink)}
.metric-label {font:11px 'DM Mono',monospace;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
div[data-testid="stMetric"] {background:white;border:1px solid var(--line);padding:14px;border-radius:3px}
div[data-testid="stMetricLabel"] {color:var(--muted)}
.stButton>button, .stDownloadButton>button {border-radius:2px;border:1px solid #343d35;background:#343d35;color:#fff;min-height:2.7rem}
.stButton>button:hover,.stDownloadButton>button:hover {background:#4c5b50;color:white;border-color:#4c5b50}
div[data-testid="stFileUploader"] {background:#fff;border:1px dashed #bcb9ad;padding:1rem}
footer {visibility:hidden}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">Independent AI performance verification</div>
  <h1>Test the numbers.<br>Trust the evidence.</h1>
  <p class="sub">Recalculate reported model-performance metrics from row-level evaluation records. Identify discrepancies, inspect dataset structure and export a reproducible review.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Evaluation settings")
    positive_label = st.selectbox("Positive class", [1, 0], index=0,
                                  help="The class treated as positive when calculating precision, recall, F1 and specificity.")
    tolerance = st.number_input("Allowed metric difference", min_value=0.0, max_value=1.0,
                                value=0.005, step=0.001, format="%.3f",
                                help="Absolute difference allowed between reported and recalculated values.")
    st.divider()
    st.caption("Processing takes place in this app session. Do not submit confidential deal data unless your deployment and data-handling terms have been reviewed.")

left, right = st.columns([1.15, .85], gap="large")
with left:
    st.markdown("### 01 — Evaluation records")
    csv_file = st.file_uploader("Upload evaluation CSV", type=["csv"], help="Required columns: record_id, split, actual, predicted")
    st.caption("Required fields: record_id · split · actual · predicted")
with right:
    st.markdown("### 02 — Reported claims")
    json_file = st.file_uploader("Upload reported-metrics JSON", type=["json"], help="Optional. Compares reported metrics against recalculated results.")
    st.caption("Optional fields: positive_label, tolerance, metrics")

st.markdown("---")
if csv_file is None:
    st.info("Upload an evaluation CSV to begin. Use the sample files in the repository's examples folder to test the workflow.")
    st.markdown("#### What this review checks")
    c1,c2,c3 = st.columns(3)
    c1.markdown("**Metric reconstruction**\n\nAccuracy, precision, recall, F1 and specificity.")
    c2.markdown("**Record integrity**\n\nMissing fields, invalid labels, duplicate IDs and exact cross-split ID overlap.")
    c3.markdown("**Claim comparison**\n\nReported values versus deterministic recalculation.")
    st.stop()

try:
    frame = pd.read_csv(csv_file, dtype="string", keep_default_na=False)
except Exception as exc:
    st.error(f"Could not read the CSV: {exc}")
    st.stop()

st.markdown("### Evidence preview")
st.caption(f"{len(frame):,} rows · {len(frame.columns)} columns")
st.dataframe(frame.head(12), use_container_width=True, hide_index=True)

reported = {}
if json_file is not None:
    try:
        reported = load_reported_metrics(json_file.getvalue())
    except Exception as exc:
        st.error(f"Reported-metrics JSON is invalid: {exc}")
        st.stop()

try:
    result = validate_dataframe(frame, reported, positive_label, tolerance)
except Exception as exc:
    st.error(f"Validation could not be completed: {exc}")
    st.stop()

st.markdown("---")
st.markdown("### Verification results")
checks = result["checks"]
flagged = sum(c["status"] == "FLAG" for c in checks)
passed = sum(c["status"] == "PASS" for c in checks)
not_tested = sum(c["status"] == "NOT_TESTED" for c in checks)

m1,m2,m3,m4 = st.columns(4)
m1.metric("Checks passed", passed)
m2.metric("Flags", flagged)
m3.metric("Not tested", not_tested)
m4.metric("Rows evaluated", result["recalculated"]["sample_count"])

if flagged:
    st.warning(f"{flagged} check(s) need review. A flag identifies a discrepancy or evidence limitation; it is not, by itself, proof of misconduct.")
elif not_tested:
    st.info("No flags were raised by the completed checks. Some checks could not be performed.")
else:
    st.success("All configured checks passed. This applies only to the supplied evidence and checks.")

metric_cols = st.columns(5)
for col, (name, value) in zip(metric_cols, result["recalculated"]["metrics"].items()):
    with col:
        shown = "N/A" if value is None else f"{value:.3%}"
        st.metric(name.replace("_", " ").title(), shown)

cm = result["recalculated"]["confusion_matrix"]
if cm:
    st.markdown("#### Confusion matrix")
    a,b,c,d = st.columns(4)
    a.metric("True positives", cm["tp"])
    b.metric("False positives", cm["fp"])
    c.metric("True negatives", cm["tn"])
    d.metric("False negatives", cm["fn"])

st.markdown("#### Check register")
for item in checks:
    label = f"{item['status']}  ·  {item['check_id']}  ·  {item['summary']}"
    with st.expander(label, expanded=item["status"] == "FLAG"):
        if item["details"]:
            for detail in item["details"]:
                st.write(f"• {detail}")
        else:
            st.caption("No additional detail.")

st.markdown("#### Scope and limitations")
for limitation in result["limitations"]:
    st.write(f"• {limitation}")

st.markdown("---")
st.markdown("### Export evidence")
st.caption("The exports contain the supplied file name, row counts, configuration, calculated values and check register. Review them before sharing.")
json_bytes = json.dumps(result, indent=2).encode("utf-8")
html_bytes = render_html_report(result).encode("utf-8")
d1,d2 = st.columns(2)
with d1:
    st.download_button("Download JSON evidence", json_bytes, file_name="evaluation-verification-report.json",
                       mime="application/json", use_container_width=True)
with d2:
    st.download_button("Download HTML report", html_bytes, file_name="evaluation-verification-report.html",
                       mime="text/html", use_container_width=True)

st.caption("AI Evaluation Evidence Validator · Deterministic calculations · Human review required")
