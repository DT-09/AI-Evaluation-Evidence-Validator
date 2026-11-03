from datetime import datetime, timezone
import io, json
import pandas as pd
import streamlit as st
from dealtie.extract import extract_excel, extract_pdf
from dealtie.reconcile import reconcile

st.set_page_config(page_title="DealTie | Financial Evidence Reconciliation",layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono&family=DM+Sans:wght@400;500;600&family=Playfair+Display&display=swap');
.stApp{background:#f2efe7;color:#24251f}.block-container{max-width:1380px;padding-top:2rem}
h1,h2,h3{font-family:'Playfair Display',serif!important;font-weight:400!important}
.brand{font:11px 'DM Mono';letter-spacing:.2em;color:#46695d}.panel{background:#fbfaf6;border:1px solid #d9d5c9;padding:18px;margin:12px 0}
.kicker{font:10px 'DM Mono';letter-spacing:.16em;color:#46695d;text-transform:uppercase}
</style><div class='brand'>DEALTIE / FINANCIAL EVIDENCE RECONCILIATION</div>
<h1>Make the numbers tie.<br><i>Keep the evidence attached.</i></h1>
<p>Compare selected figures across a CIM, Quality of Earnings report and valuation model. Analysts confirm extracted observations; DealTie flags inconsistencies and preserves source references.</p>""",unsafe_allow_html=True)

if "obs" not in st.session_state: st.session_state.obs=[]
if "extracts" not in st.session_state: st.session_state.extracts=[]
left,right=st.columns([1.15,.85])
with left:
    st.markdown('<div class="panel"><div class="kicker">01 / Source intake</div>',unsafe_allow_html=True)
    files=st.file_uploader("Upload PDF, XLSX, XLS or structured CSV",type=["pdf","xlsx","xls","csv"],accept_multiple_files=True)
    if st.button("Extract candidate observations",disabled=not files):
        found=[]
        for f in files:
            raw=f.getvalue()
            if f.name.lower().endswith(".pdf"): found.extend(extract_pdf(raw,f.name))
            elif f.name.lower().endswith((".xlsx",".xls")): found.extend(extract_excel(raw,f.name))
            else:
                df=pd.read_csv(io.BytesIO(raw),dtype=str).fillna("")
                required={"document","period","metric","value","unit","source_ref"}
                if required.issubset(df.columns): st.session_state.obs.extend(df.to_dict("records"))
                else: st.warning(f"{f.name}: expected columns: {', '.join(sorted(required))}")
        st.session_state.extracts=found
        st.success(f"Extracted {len(found)} candidate text/cell items. Confirm mappings below.")
    st.markdown('</div>',unsafe_allow_html=True)
with right:
    st.markdown('<div class="panel"><div class="kicker">02 / Manual observation</div>',unsafe_allow_html=True)
    with st.form("manual"):
        doc=st.text_input("Document label",placeholder="CIM v3 / QoE final / Model")
        metric=st.text_input("Metric",placeholder="Revenue / Adjusted EBITDA / Net Debt")
        period=st.text_input("Period",placeholder="FY2025 / LTM Jun-26")
        value=st.text_input("Value",placeholder="128.4")
        unit=st.text_input("Unit",placeholder="USD m / EUR m / % / x")
        ref=st.text_input("Source reference",placeholder="PDF p.18 / Model!F22")
        if st.form_submit_button("Add confirmed observation"):
            if all(x.strip() for x in [doc,metric,period,unit,ref]):
                st.session_state.obs.append({"document":doc,"metric":metric,"period":period,"value":value,"unit":unit,"source_ref":ref})
                st.success("Added.")
            else: st.error("Complete all fields except value; blank values are allowed for review.")
    st.markdown('</div>',unsafe_allow_html=True)

if st.session_state.extracts:
    st.markdown('<div class="panel"><div class="kicker">03 / Map extracted source items</div><p>Extraction is not semantic. Verify each item against the original document before comparison.</p>',unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.extracts),use_container_width=True,hide_index=True,height=230)
    ix=st.number_input("Selected extracted item (row)",1,len(st.session_state.extracts),1)-1
    item=st.session_state.extracts[int(ix)]
    st.caption(f"{item['document']} · {item['source_ref']} · {item['extracted_text'][:250]}")
    with st.form("map"):
        a,b,c=st.columns(3)
        mm=a.text_input("Confirmed metric")
        pp=b.text_input("Confirmed period")
        vv=c.text_input("Confirmed value")
        d,e=st.columns(2)
        uu=d.text_input("Confirmed unit")
        dd=e.text_input("Document label",value=item["document"])
        if st.form_submit_button("Confirm and add"):
            if all(x.strip() for x in [mm,pp,vv,uu,dd]):
                st.session_state.obs.append({"document":dd,"metric":mm,"period":pp,"value":vv,"unit":uu,"source_ref":item["source_ref"]})
                st.success("Confirmed observation added.")
            else: st.error("Complete all mapping fields.")
    st.markdown('</div>',unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="kicker">04 / Evidence ledger</div>',unsafe_allow_html=True)
if st.session_state.obs:
    st.dataframe(pd.DataFrame(st.session_state.obs),use_container_width=True,hide_index=True)
    a,b=st.columns(2)
    if a.button("Run reconciliation",use_container_width=True):
        st.session_state.results=reconcile(st.session_state.obs)
    if b.button("Clear evidence",use_container_width=True):
        st.session_state.obs=[]
        st.session_state.pop("results",None)
        st.rerun()
else:
    st.info("No confirmed observations. Load the synthetic example or add observations.")
    if st.button("Load synthetic example"):
        st.session_state.obs=[
            {"document":"CIM v2","metric":"Revenue","period":"FY2025","value":"128.4","unit":"USD m","source_ref":"PDF p.18"},
            {"document":"QoE final","metric":"Revenue","period":"FY2025","value":"126.9","unit":"USD m","source_ref":"PDF p.11"},
            {"document":"Valuation Model","metric":"Revenue","period":"FY2025","value":"128.4","unit":"USD m","source_ref":"Operating Model!F22"},
            {"document":"CIM v2","metric":"Net Debt","period":"LTM Jun-26","value":"34.2","unit":"USD m","source_ref":"PDF p.39"},
            {"document":"Valuation Model","metric":"Net Debt","period":"LTM Jun-26","value":"34.2","unit":"EUR m","source_ref":"Bridge!D31"}]
        st.rerun()
st.markdown('</div>',unsafe_allow_html=True)

if st.session_state.get("results"):
    results=st.session_state.results
    st.markdown("## Reconciliation findings")
    st.dataframe(pd.DataFrame([{k:r[k] for k in ["metric","period","status","explanation","source_count"]} for r in results]),use_container_width=True,hide_index=True)
    for r in results:
        with st.expander(f"{r['status']} · {r['metric']} · {r['period']}"):
            st.write(r["explanation"])
            st.dataframe(pd.DataFrame([{"Document":o["document"],"Value":o.get("value"),"Unit":o["unit"],"Source":o.get("source_ref","")} for o in r["observations"]]),use_container_width=True,hide_index=True)
    payload={"product":"DealTie","generated_at_utc":datetime.now(timezone.utc).isoformat(),"limitations":["Analyst confirmation required.","No semantic matching, currency conversion or accounting judgement.","A mismatch is an investigation lead, not proof of loss."],"findings":results}
    st.download_button("Download evidence register JSON",json.dumps(payload,indent=2).encode(),"dealtie-evidence-register.json","application/json")
st.caption("Synthetic data only. Do not upload confidential deal materials. Not an audit, QoE conclusion, valuation opinion or transaction advice.")
