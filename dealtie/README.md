# DealTie — Financial Evidence Reconciliation

DealTie is an analyst workbench for a narrow pre-issue financial tie-out: compare selected figures across a CIM, Quality of Earnings report and valuation model, then retain the source trail for each observation.

## Run locally

From the repository root:

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS / Linux:
source .venv/bin/activate

python -m pip install -r dealtie/requirements.txt
streamlit run dealtie/app.py
```

## Try the synthetic case

Upload `dealtie/sample-data/synthetic-observations.csv` in the app, or use **Load synthetic example**. The sample intentionally contains a revenue difference and a net-debt unit conflict. All figures and source references are fictional.

## Supported workflow

1. Upload selectable-text PDF, XLSX, XLS or structured CSV files (15 MB per file in the app).
2. Extract PDF text lines or non-empty spreadsheet cells with page/sheet/cell references.
3. Manually confirm metric, period, value and unit for extracted items.
4. Compare observations by normalized metric and period.
5. Review the source-level observations and export JSON findings plus a flat CSV observation register.

### CSV schema

Required columns:

`document,period,metric,value,unit,source_ref`

The document field may be blank; the uploaded filename is then used. Metric, period, unit and source reference are required. Value may be blank so the app can surface an incomplete observation.

## Reconciliation rules

- `TIED`: all supplied numeric values agree within the configured tolerance.
- `VALUE_MISMATCH`: the numeric spread exceeds tolerance.
- `UNIT_MISMATCH`: source units differ; no conversion is attempted.
- `MISSING_OR_NON_NUMERIC`: a value is missing/non-numeric, or a required unit/source reference is absent.
- `INSUFFICIENT_COVERAGE`: fewer than two distinct documents are represented.

Comparison is deterministic. It does not infer that two differently named metrics are equivalent. It does not establish which source is correct.

## Tests

```bash
PYTHONPATH=. python -m unittest discover -s dealtie/tests -v
python -m compileall -q dealtie
```

## Deployment

The Streamlit workbench can be deployed as a Streamlit Community Cloud app by selecting this repository, setting the app file path to `dealtie/app.py`, and using `dealtie/requirements.txt` as the dependency file. A deployment has not been configured by this repository.

The static marketing site is `website/index.html`. It can be deployed as a Cloudflare Pages project with `website` as the build output directory and no build command. A live deployment is not implied by a successful GitHub commit; verify the Pages project and deployment status separately.

## Data handling and boundaries

- Do not upload confidential live transaction materials to this prototype.
- Use synthetic or appropriately redacted/authorised data only.
- No OCR for scanned PDFs, formula evaluation, semantic matching, currency conversion, accounting judgement, audit procedures or QoE conclusions.
- No authentication, hosted multi-user controls, encryption-at-rest, audit-grade history or secure deal-room integration.
- A mismatch is an investigation lead, not proof of error, misstatement, overpayment or financial loss.
- This is not production diligence software, an audit opinion, valuation opinion, legal opinion or transaction advice.
- Any paid engagement, contract, payment, confidentiality and client-data arrangements require an appropriately authorised business representative. A qualified finance professional must supervise substantive financial interpretation.
