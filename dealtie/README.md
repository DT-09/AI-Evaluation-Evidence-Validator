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

Use **Load synthetic example** in the app or upload `dealtie/sample-data/synthetic-observations.csv`. All figures and source references are fictional.

## Working workflow

1. Upload selectable-text PDF, XLSX, XLS or structured CSV files (15 MB per file).
2. Extract PDF text lines and spreadsheet cell values with page/sheet/cell references.
3. Confirm extracted observations in a batch review grid. No extracted text is treated as a financial metric until the analyst confirms its mapping.
4. Add observations manually or import a structured CSV ledger.
5. Set the numeric comparison tolerance and run deterministic comparisons by metric and period.
6. Review findings and source observations; export a JSON evidence register and flat CSV.

### CSV schema

Required columns:

`document,period,metric,value,unit,source_ref`

The document field may be blank; the uploaded filename is then used. Metric, period, unit and source reference are required. Value may be blank so an incomplete observation is visible.

## Reconciliation statuses

- `TIED`: all supplied numeric values agree within the configured tolerance.
- `VALUE_MISMATCH`: the numeric spread exceeds tolerance.
- `UNIT_MISMATCH`: source units differ; no conversion is attempted.
- `MISSING_OR_NON_NUMERIC`: a value, unit or source reference is missing or a value is non-numeric.
- `DUPLICATE_SOURCE_ENTRY`: the same document/source reference appears more than once for a metric and period.
- `INSUFFICIENT_COVERAGE`: fewer than two distinct documents are represented.

Values such as `(100)`, `38.2%` and `4.2x` are parsed as numeric values while retaining the stated unit. The tool does not infer scale, currency, period equivalence or which source is correct.

## Tests

```bash
PYTHONPATH=. python -m unittest discover -s dealtie/tests -v
python -m compileall -q dealtie
```

## Deployment

The Streamlit workbench can be deployed as a Streamlit Community Cloud app by selecting this repository, setting the app file path to `dealtie/app.py`, and using `dealtie/requirements.txt` as the dependency file. Deployment is not performed by a GitHub commit; verify the app URL and a complete synthetic run after publishing.

The static marketing site is `website/index.html`. It can be deployed as a Cloudflare Pages project with `website` as the build output directory and no build command. Verify the Pages project and live deployment separately.

## Data handling and boundaries

- Prototype only: synthetic or appropriately redacted/authorised data. Do not upload confidential live transaction materials.
- PDF extraction reads selectable text only; scanned-PDF OCR is not implemented.
- Excel extraction captures non-empty cell values; it does not evaluate formulas or understand workbook logic.
- No semantic metric matching, currency conversion, accounting judgement, audit procedures or QoE conclusions.
- No authentication, hosted multi-user controls, encryption-at-rest, audit-grade history or secure deal-room integration.
- A mismatch is an investigation lead, not proof of error, misstatement, overpayment or financial loss.
- This is not an audit opinion, valuation opinion, legal opinion or transaction recommendation.
- Any paid engagement, contract, payment, confidentiality and client-data arrangements require an appropriately authorised business representative. A qualified finance professional must supervise substantive financial interpretation.
