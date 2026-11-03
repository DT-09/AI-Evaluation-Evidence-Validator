from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import io
import json

import pandas as pd
import streamlit as st

from dealtie.extract import extract_excel, extract_pdf
from dealtie.reconcile import reconcile

st.set_page_config(page_title="DealTie | Financial Evidence Reconciliation", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono&family=DM+Sans:wght@400;500;600&family=Playfair+Display&display=swap');
.stApp{background:#f2efe7;color:#24251f}.block-container{max-width:1380px;padding-top:2rem}
h1,h2,h3{font-family:'Playfair Display',serif!important;font-weight:400!important}
.brand{font:11px 'DM Mono';letter-spacing:.2em;color:#46695d}.panel{background:#fbfaf6;border:1px solid #d9d5c9;padding:18px;margin:12px 0}
.kicker{font:10px 'DM Mono';letter-spacing:.16em;color:#46695d;text-transform:uppercase}
div[data-testid="stDataFrame"],div[data-testid="stDataEditor"]{border:1px solid #d9d5c9}
</style><div class='brand'>DEALTIE / FINANCIAL EVIDENCE RECONCILIATION</div>
<h1>Make the numbers tie.<br><i>Keep the evidence attached.</i></h1>
<p>Compare analyst-confirmed figures across transaction documents. DealTie flags inconsistencies and preserves source references; it does not interpret the accounts.</p>""", unsafe_allow_html=True)

REQUIRED = {"document", "period", "metric", "value", "unit", "source_ref"}
MAX_FILE_BYTES = 15 * 1024 * 1024
def invalidate_results():
    st.session_state.results = None


def clean_csv_rows(frame, filename):
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    rows = []
    for line, item in enumerate(frame[list(REQUIRED)].to_dict("records"), start=2):
        row = {k: ("" if pd.isna(v) else str(v).strip()) for k, v in item.items()}
        if not row["document"]:
            row["document"] = filename
        if not row["metric"] or not row["period"]:
            raise ValueError(f"Row {line}: metric and period are required.")
        if not row["unit"] or not row["source_ref"]:
            raise ValueError(f"Row {line}: unit and source_ref are required.")
        rows.append(row)
    return rows


def load_synthetic():
    st.session_state.extracts = []
    st.session_state.mapping_rows = []
    st.session_state.obs = [
        {"document":"CIM v2","metric":"Revenue","period":"FY2025","value":"128.4","unit":"USD m","source_ref":"PDF p.18"},
        {"document":"QoE final","metric":"Revenue","period":"FY2025","value":"126.9","unit":"USD m","source_ref":"PDF p.11"},
        {"document":"Valuation Model","metric":"Revenue","period":"FY2025","value":"128.4","unit":"USD m","source_ref":"Operating Model!F22"},
        {"document":"CIM v2","metric":"Net Debt","period":"LTM Jun-26","value":"34.2","unit":"USD m","source_ref":"PDF p.39"},
        {"document":"Valuation Model","metric":"Net Debt","period":"LTM Jun-26","value":"34.2","unit":"EUR m","source_ref":"Bridge!D31"},
        {"document":"CIM v2","metric":"Gross Margin","period":"FY2025","value":"38.2","unit":"%","source_ref":"PDF p.20"},
        {"document":"QoE final","metric":"Gross Margin","period":"FY2025","value":"38.2","unit":"%","source_ref":"PDF p.15"},
        {"document":"Valuation Model","metric":"Gross Margin","period":"FY2025","value":"38.2","unit":"%","source_ref":"Summary!F31"},
    ]
    invalidate_results()


for key, default in {
    "obs": [], "extracts": [], "results": None, "import_errors": [],
    "source_names": [], "mapping_rows": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

left, right = st.columns([1.15, .85])
with left:
    st.markdown('<div class="panel"><div class="kicker">01 / Source intake</div>', unsafe_allow_html=True)
    files = st.file_uploader(
        "Upload PDF, XLSX, XLS or structured CSV",
        type=["pdf", "xlsx", "xls", "csv"],
        accept_multiple_files=True,
        help="15 MB per file. Use synthetic or properly redacted/authorised files only."
    )
    if st.button("Extract candidate observations", disabled=not files):
        found, csv_rows, errors = [], [], []
        for file in files:
            try:
                raw = file.getvalue()
                if len(raw) > MAX_FILE_BYTES:
                    raise ValueError("File exceeds the 15 MB prototype limit.")
                lower = file.name.lower()
                if lower.endswith(".pdf"):
                    found.extend(extract_pdf(raw, file.name))
                elif lower.endswith((".xlsx", ".xls")):
                    found.extend(extract_excel(raw, file.name))
                elif lower.endswith(".csv"):
                    frame = pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False)
                    csv_rows.extend(clean_csv_rows(frame, file.name))
            except Exception as exc:
                errors.append(f"{file.name}: {type(exc).__name__}: {exc}")
        st.session_state.extracts = found
        st.session_state.mapping_rows = []
        st.session_state.obs.extend(csv_rows)
        st.session_state.import_errors = errors
        st.session_state.source_names = [f.name for f in files]
        invalidate_results()
        if errors:
            st.warning(f"Processed with {len(errors)} file issue(s). {len(found)} PDF/Excel items and {len(csv_rows)} CSV observations were imported; review the errors below.")
        else:
            st.success(f"Extracted {len(found)} PDF/Excel text or cell items and imported {len(csv_rows)} structured CSV observations.")
    for error in st.session_state.import_errors:
        st.error(error)
    st.caption("PDF extraction reads selectable text. Excel extraction captures non-empty cell values. Neither identifies financial meaning.")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel"><div class="kicker">02 / Manual observation</div>', unsafe_allow_html=True)
    with st.form("manual_observation", clear_on_submit=True):
        doc = st.text_input("Document label", placeholder="CIM v3 / QoE final / Model")
        metric = st.text_input("Metric", placeholder="Revenue / Adjusted EBITDA / Net Debt")
        period = st.text_input("Period", placeholder="FY2025 / LTM Jun-26")
        value = st.text_input("Value", placeholder="128.4")
        unit = st.text_input("Unit", placeholder="USD m / EUR m / % / x")
        ref = st.text_input("Source reference", placeholder="PDF p.18 / Model!F22")
        if st.form_submit_button("Add confirmed observation"):
            if all(x.strip() for x in [doc, metric, period, unit, ref]):
                st.session_state.obs.append({
                    "document":doc.strip(), "metric":metric.strip(), "period":period.strip(),
                    "value":value.strip(), "unit":unit.strip(), "source_ref":ref.strip()
                })
                invalidate_results()
                st.success("Observation added.")
            else:
                st.error("Document, metric, period, unit and source reference are required. Value may be blank for review.")
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.extracts:
    st.markdown('<div class="panel"><div class="kicker">03 / Batch-confirm extracted source items</div><p>Map several extracted items in one pass. Only checked rows are added to the evidence ledger. Extraction is literal, not semantic.</p>', unsafe_allow_html=True)
    if "mapping_rows" not in st.session_state or len(st.session_state.mapping_rows) != len(st.session_state.extracts):
        st.session_state.mapping_rows = [
            {"confirm":False, "document":item["document"], "metric":"", "period":"", "value":"", "unit":"", "source_ref":item["source_ref"], "extracted_text":item["extracted_text"]}
            for item in st.session_state.extracts
        ]
    mapping = pd.DataFrame(st.session_state.mapping_rows)
    edited = st.data_editor(
        mapping,
        key="mapping_editor",
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        height=360,
        column_config={
            "confirm":st.column_config.CheckboxColumn("Add", help="Tick only after checking the original source."),
            "document":st.column_config.TextColumn("Document", required=True),
            "metric":st.column_config.TextColumn("Confirmed metric"),
            "period":st.column_config.TextColumn("Confirmed period"),
            "value":st.column_config.TextColumn("Confirmed value"),
            "unit":st.column_config.TextColumn("Confirmed unit"),
            "source_ref":st.column_config.TextColumn("Source reference", disabled=True),
            "extracted_text":st.column_config.TextColumn("Extracted text", disabled=True, width="large"),
        }
    )
    st.session_state.mapping_rows = edited.to_dict("records")
    if st.button("Add checked observations", type="primary"):
        selected = edited[edited["confirm"] == True]
        additions, issues = [], []
        for idx, row in selected.iterrows():
            fields = [str(row.get(k, "")).strip() for k in ["document","metric","period","value","unit","source_ref"]]
            if not all(fields):
                issues.append(f"Row {idx + 1}: complete document, metric, period, value and unit before adding.")
                continue
            additions.append(dict(zip(["document","metric","period","value","unit","source_ref"], fields)))
        if issues:
            for issue in issues:
                st.error(issue)
        elif not additions:
            st.warning("No rows were checked.")
        else:
            st.session_state.obs.extend(additions)
            st.session_state.extracts = []
            st.session_state.mapping_rows = []
            invalidate_results()
            st.success(f"Added {len(additions)} confirmed observation(s).")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="kicker">04 / Evidence ledger</div>', unsafe_allow_html=True)
if st.session_state.obs:
    ledger = pd.DataFrame(st.session_state.obs)
    st.caption(f"{len(ledger)} observation(s) · {ledger['document'].nunique()} distinct source document(s)")
    st.dataframe(ledger, use_container_width=True, hide_index=True)
    with st.expander("Remove an observation"):
        index = st.selectbox(
            "Observation to remove", options=range(len(st.session_state.obs)),
            format_func=lambda i: f"{i + 1}. {st.session_state.obs[i]['metric']} · {st.session_state.obs[i]['period']} · {st.session_state.obs[i]['document']}"
        )
        if st.button("Remove selected observation"):
            st.session_state.obs.pop(index)
            invalidate_results()
            st.rerun()
    tol_col, run_col, sample_col, clear_col = st.columns([1,1,1,1])
    tolerance_text = tol_col.text_input("Numeric tolerance", value="0.01", help="Absolute tolerance in the metric's stated unit. No scale or currency conversion.")
    if run_col.button("Run reconciliation", type="primary", use_container_width=True):
        try:
            tolerance = Decimal(tolerance_text.strip())
            st.session_state.results = reconcile(st.session_state.obs, tolerance=tolerance)
            st.session_state.applied_tolerance = str(tolerance)
        except (InvalidOperation, ValueError) as exc:
            st.error(f"Invalid tolerance: {exc}")
    if sample_col.button("Reset to sample", use_container_width=True):
        load_synthetic()
        st.rerun()
    if clear_col.button("Clear evidence", use_container_width=True):
        st.session_state.obs = []
        st.session_state.extracts = []
        st.session_state.mapping_rows = []
        st.session_state.import_errors = []
        invalidate_results()
        st.rerun()
else:
    st.info("No confirmed observations. Add one manually, upload a structured CSV, or load the synthetic example.")
    if st.button("Load synthetic example"):
        load_synthetic()
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.results is not None:
    results = st.session_state.results
    st.markdown("## Reconciliation findings")
    counts = pd.Series([r["status"] for r in results]).value_counts() if results else pd.Series(dtype=int)
    metric_cols = st.columns(4)
    metric_cols[0].metric("Metrics reviewed", len(results))
    metric_cols[1].metric("Value mismatches", int(counts.get("VALUE_MISMATCH", 0)))
    metric_cols[2].metric("Unit / duplicate issues", int(counts.get("UNIT_MISMATCH", 0) + counts.get("DUPLICATE_SOURCE_ENTRY", 0)))
    metric_cols[3].metric("Tied", int(counts.get("TIED", 0)))
    if results:
        st.dataframe(pd.DataFrame([{
            "Metric":r["metric"], "Period":r["period"], "Status":r["status"],
            "Sources":r["source_count"], "Observations":r["observation_count"],
            "Explanation":r["explanation"]
        } for r in results]), use_container_width=True, hide_index=True)
        for finding in results:
            with st.expander(f"{finding['status']} · {finding['metric']} · {finding['period']}"):
                st.write(finding["explanation"])
                st.dataframe(pd.DataFrame([{
                    "Document":o["document"], "Value":o.get("value"),
                    "Unit":o["unit"], "Source reference":o.get("source_ref", "")
                } for o in finding["observations"]]), use_container_width=True, hide_index=True)
    else:
        st.info("No comparable groups were found. Check that each observation has a document, metric and period.")
    payload = {
        "product":"DealTie", "schema_version":"1.1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "scope":"Analyst-confirmed observation comparison",
        "tolerance":st.session_state.get("applied_tolerance", "0.01"),
        "limitations":[
            "Analyst confirmation is required.",
            "No semantic matching, formula evaluation, currency conversion or accounting judgement.",
            "A mismatch is an investigation lead, not proof of error, misstatement or financial loss."
        ],
        "findings":results
    }
    st.download_button(
        "Download evidence register (JSON)", json.dumps(payload, indent=2).encode("utf-8"),
        file_name="dealtie-evidence-register.json", mime="application/json"
    )
    flat = []
    for finding in results:
        for observation in finding["observations"]:
            flat.append({
                "metric":finding["metric"], "period":finding["period"],
                "status":finding["status"], "explanation":finding["explanation"],
                "document":observation["document"], "value":observation.get("value"),
                "unit":observation["unit"], "source_ref":observation.get("source_ref", "")
            })
    st.download_button(
        "Download observation register (CSV)",
        pd.DataFrame(flat).to_csv(index=False).encode("utf-8"),
        file_name="dealtie-observation-register.csv", mime="text/csv"
    )

st.caption("Prototype only. Synthetic or redacted/authorised data only. Do not upload confidential deal materials. Not an audit, QoE conclusion, valuation opinion or transaction advice.")
