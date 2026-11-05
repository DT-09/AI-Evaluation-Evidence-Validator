from decimal import Decimal, InvalidOperation
import json
import pandas as pd
import streamlit as st

from dealtie.change_impact import analyze_version_impact

st.markdown("""
<style>
.stApp{background:#f2efe7;color:#24251f}.block-container{max-width:1200px;padding-top:2rem}
h1,h2,h3{font-family:Georgia,serif!important;font-weight:400!important}
.kicker{font:10px monospace;letter-spacing:.16em;color:#536a59;text-transform:uppercase}
.panel{background:#fbfaf6;border:1px solid #d9d5c9;padding:18px;margin:12px 0}
</style>
<div class="kicker">DEALTIE / VERSION CHANGE INTELLIGENCE</div>
""",unsafe_allow_html=True)
st.title("Trace the change. Find the references.")
st.write("Compare two analyst-confirmed versions of a source document family, then inspect downstream documents that still carry the prior value or show another value.")
st.warning("This is deterministic comparison, not semantic document understanding. A stale candidate is a review lead, not proof of an error. Use synthetic or properly redacted and authorised material only.")

SAMPLE = [
    {"document_family":"QoE","version":"v1","document":"QoE report v1","metric":"Adjusted EBITDA","period":"FY2025","value":"18.2","unit":"USD m","source_ref":"PDF p.12"},
    {"document_family":"QoE","version":"v2","document":"QoE report v2","metric":"Adjusted EBITDA","period":"FY2025","value":"17.6","unit":"USD m","source_ref":"PDF p.13"},
    {"document_family":"CIM","version":"v1","document":"CIM v1","metric":"Adjusted EBITDA","period":"FY2025","value":"18.2","unit":"USD m","source_ref":"PDF p.21"},
    {"document_family":"Valuation model","version":"v4","document":"Valuation model v4","metric":"Adjusted EBITDA","period":"FY2025","value":"17.6","unit":"USD m","source_ref":"Summary!D8"},
    {"document_family":"Management presentation","version":"v2","document":"Management presentation v2","metric":"Adjusted EBITDA","period":"FY2025","value":"18.2","unit":"USD m","source_ref":"Slide 14"},
    {"document_family":"QoE","version":"v1","document":"QoE report v1","metric":"Revenue","period":"FY2025","value":"126.9","unit":"USD m","source_ref":"PDF p.11"},
    {"document_family":"QoE","version":"v2","document":"QoE report v2","metric":"Revenue","period":"FY2025","value":"126.9","unit":"USD m","source_ref":"PDF p.11"},
    {"document_family":"CIM","version":"v1","document":"CIM v1","metric":"Revenue","period":"FY2025","value":"126.9","unit":"USD m","source_ref":"PDF p.18"},
]
REQUIRED={"document_family","version","document","metric","period","value","unit","source_ref"}
if "impact_rows" not in st.session_state:
    st.session_state.impact_rows=[]

left,right=st.columns([1,1])
with left:
    st.markdown('<div class="panel"><div class="kicker">01 / Source observations</div>',unsafe_allow_html=True)
    uploaded=st.file_uploader("Upload a CSV observation register",type=["csv"],help="Required columns: "+", ".join(sorted(REQUIRED)))
    if st.button("Load synthetic version case"):
        st.session_state.impact_rows=SAMPLE.copy()
        st.rerun()
    if uploaded:
        try:
            frame=pd.read_csv(uploaded,dtype=str,keep_default_na=False)
            missing=REQUIRED-set(frame.columns)
            if missing:
                st.error("Missing columns: "+", ".join(sorted(missing)))
            else:
                st.session_state.impact_rows=frame[list(REQUIRED)].to_dict("records")
                st.success(f"Loaded {len(frame)} observation rows locally.")
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")
    st.caption("CSV is processed in this Streamlit session. Do not upload confidential deal materials to this prototype.")
    st.markdown('</div>',unsafe_allow_html=True)
with right:
    st.markdown('<div class="panel"><div class="kicker">02 / Version comparison</div>',unsafe_allow_html=True)
    baseline=st.text_input("Baseline version",value="v1")
    current=st.text_input("Current version",value="v2")
    tolerance=st.text_input("Absolute tolerance",value="0.01",help="Applied in the explicitly stated unit. No scale conversion.")
    run=st.button("Analyse version impact",type="primary",use_container_width=True,disabled=not st.session_state.impact_rows)
    st.markdown('</div>',unsafe_allow_html=True)

if st.session_state.impact_rows:
    st.markdown('<div class="panel"><div class="kicker">03 / Observation register</div>',unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.impact_rows),use_container_width=True,hide_index=True)
    st.markdown('</div>',unsafe_allow_html=True)

if run:
    try:
        findings=analyze_version_impact(st.session_state.impact_rows,baseline,current,tolerance)
        st.session_state.impact_findings=findings
        st.session_state.impact_error=None
    except (ValueError,InvalidOperation) as exc:
        st.session_state.impact_error=str(exc)
        st.session_state.impact_findings=None

if st.session_state.get("impact_error"):
    st.error(st.session_state.impact_error)
if st.session_state.get("impact_findings") is not None:
    findings=st.session_state.impact_findings
    stale=sum(item["stale_candidate_count"] for item in findings)
    c1,c2,c3=st.columns(3)
    c1.metric("Source changes detected",len(findings))
    c2.metric("Stale candidates",stale)
    c3.metric("Downstream references",sum(len(item["downstream_references"]) for item in findings))
    if not findings:
        st.info("No changed source metric-period pairs were found across the selected versions.")
    for item in findings:
        with st.expander(f"{item['source_family']} · {item['metric']} · {item['period']} · {item['baseline_value']} → {item['current_value']}",expanded=True):
            st.write(item["interpretation"])
            st.write(f"Change: {item['change']} {item['unit']}")
            st.caption("Baseline sources")
            st.dataframe(pd.DataFrame(item["baseline_sources"]),use_container_width=True,hide_index=True)
            st.caption("Current sources")
            st.dataframe(pd.DataFrame(item["current_sources"]),use_container_width=True,hide_index=True)
            if item["downstream_references"]:
                st.caption("Downstream references for human review")
                st.dataframe(pd.DataFrame(item["downstream_references"]),use_container_width=True,hide_index=True)
            else:
                st.caption("No exact downstream metric-period matches were supplied.")
    payload={"product":"DealTie","analysis":"deterministic version impact","baseline_version":baseline,"current_version":current,"tolerance":tolerance,"limitations":["Exact metric and period matching only.","No semantic matching, unit conversion, scale conversion or source-authority inference.","Stale candidates are review leads, not confirmed errors."],"changes":findings}
    st.download_button("Download version impact register (JSON)",json.dumps(payload,indent=2).encode(),file_name="dealtie-version-impact.json",mime="application/json")
    flat=[{"source_family":x["source_family"],"metric":x["metric"],"period":x["period"],"baseline_value":x["baseline_value"],"current_value":x["current_value"],"downstream_family":r["document_family"],"downstream_version":r["version"],"document":r["document"],"value":r["value"],"unit":r["unit"],"source_ref":r["source_ref"],"state":r["state"]} for x in findings for r in x["downstream_references"]]
    st.download_button("Download downstream review list (CSV)",pd.DataFrame(flat).to_csv(index=False).encode(),file_name="dealtie-downstream-review.csv",mime="text/csv")
st.caption("Prototype only · Human review required · No audit, QoE, valuation or transaction opinion.")
