# DealTie — Financial Evidence Reconciliation

A focused analyst workbench for comparing selected figures across a Confidential Information Memorandum (CIM), Quality of Earnings (QoE) report and valuation model. It preserves source references and flags value differences, unit conflicts, missing values and incomplete source coverage.

## Run
From the repository root:

```bash
pip install -r dealtie/requirements.txt
streamlit run dealtie/app.py
```

## Workflow
1. Upload PDF, XLSX, XLS or structured CSV sources.
2. Extract selectable PDF text or workbook cell values.
3. Manually map each relevant item to a metric, period, numeric value and unit. Verify against the source.
4. Reconcile confirmed observations and inspect source-linked findings.
5. Export a JSON evidence register.

## CSV schema
`document,period,metric,value,unit,source_ref`

## Boundaries
- PDF extraction reads selectable text only; scanned-PDF OCR is not included.
- Excel intake lists cell values with sheet/cell references; it does not infer metric labels or periods.
- No semantic metric matching, formula evaluation, currency conversion, accounting judgement, audit procedures or legal review.
- A mismatch is an investigation lead, not proof of error, overstatement or financial loss.
- No authentication, hosted multi-user controls, encryption-at-rest, audit-grade history or secure deal-room integration. Do not upload confidential deal files.
- Sample data is synthetic. This is a prototype, not a production diligence system.

## Tests
```bash
PYTHONPATH=. python -m unittest discover -s dealtie/tests -v
```
