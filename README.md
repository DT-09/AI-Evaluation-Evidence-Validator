# DealTie — Financial Evidence Reconciliation

DealTie is an analyst workbench for a narrow, pre-issue financial consistency review across a Confidential Information Memorandum (CIM), Quality of Earnings (QoE) report and valuation model. It compares analyst-confirmed observations, identifies exceptions and preserves the source trail for qualified human review.

## The buyer's job

A boutique M&A advisory or financial diligence team needs to check whether selected headline metrics remain consistent across the transaction document pack before material is circulated or relied upon. DealTie turns that tie-out into a traceable observation ledger, prioritised exception register and exportable review record.

**The product is not an audit, QoE engagement, accounting opinion, valuation opinion or transaction recommendation.** A mismatch is an investigation lead—not proof of an error, misstatement, financial loss or recoverable amount.

## Run the workbench

From the repository root:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS / Linux: source .venv/bin/activate
python -m pip install -r dealtie/requirements.txt
streamlit run dealtie/app.py
```

Use **Load synthetic example** to inspect the complete workflow without client data.

## Implemented workflow

1. Upload selectable-text PDF, XLSX, XLS or structured CSV source material (15 MB per file).
2. Extract literal PDF lines and spreadsheet cell values with page, sheet and cell references.
3. Confirm the metric, period, value and unit before an extracted item enters the evidence ledger.
4. Add or remove observations manually; import a structured CSV ledger.
5. Compare observations using an explicit numeric tolerance and deterministic rules.
6. Review every finding alongside its source observations.
7. Export JSON, CSV and a readable HTML review report.

Extraction does not determine financial meaning. The analyst remains responsible for mapping and interpretation.

## Reconciliation statuses

- `TIED`: all supplied numeric values agree within the configured tolerance.
- `VALUE_MISMATCH`: the numeric spread exceeds tolerance.
- `UNIT_MISMATCH`: stated units differ; no conversion is attempted.
- `MISSING_OR_NON_NUMERIC`: a required value, unit or source reference is missing or non-numeric.
- `DUPLICATE_SOURCE_ENTRY`: the same document/source reference appears more than once for a metric and period.
- `INSUFFICIENT_COVERAGE`: fewer than two distinct source documents are represented.

The engine does not infer scale, currency, period equivalence, source hierarchy or which figure is correct. Findings are ordered by a transparent workflow triage priority: comparison conflicts first, evidence-quality issues next, incomplete coverage after that, and tied metrics last. This is not a financial materiality or risk score.

## CSV schema

Required columns: `document,period,metric,value,unit,source_ref`.

The document field may be blank; the uploaded filename is then used. Metric, period, unit and source reference are required. A blank value is retained as an incomplete observation for review.

## Tests

```bash
PYTHONPATH=. python -m unittest discover -s dealtie/tests -v
python -m compileall -q dealtie
```

## Deployment

- Workbench: deploy as a Streamlit Community Cloud app, selecting this repository, app path `dealtie/app.py`, and dependency file `dealtie/requirements.txt`.
- Public site: deploy `website/` to Cloudflare Pages with no build command and `website` as the output directory. The private inquiry form requires the encrypted Cloudflare environment variables documented in [the deployment checklist](commercial/deployment-checklist.md).

A successful repository build is not proof of a successful live deployment. Verify the public site and run a full synthetic case in the deployed workbench after publishing.

## Data handling and professional boundaries

- The current workbench is a prototype. Use synthetic or properly redacted, authorised data only.
- Do not upload confidential transaction materials. The prototype does not provide authentication, role-based access, encryption-at-rest, secure deal-room controls, audit-grade history or multi-user review.
- PDF extraction reads selectable text only; scanned-PDF OCR is not implemented.
- Excel extraction captures non-empty cell values; it does not evaluate formulas or understand workbook logic.
- No semantic metric matching, currency conversion, accounting judgement, audit procedures or QoE conclusions are performed.
- Any substantive financial interpretation must be supervised and approved by a qualified finance professional.
- Any engagement, contracting, payment, confidentiality and client-data arrangements require an appropriately authorised adult/business representative.

## Commercial status

The initial offer is a tightly scoped, paid, analyst-supervised tie-out review for a boutique advisory or diligence team. Scope and fee are agreed only after a non-confidential scoping discussion. No customer, revenue, savings or validated willingness to pay is claimed.

See [the product direction](PRODUCT_DIRECTION.md), [the paid pilot offer](commercial/dealtie-paid-pilot.md), [the deployment checklist](commercial/deployment-checklist.md), [the M&A tie-out service page](website/cim-qoe-model-tie-out.html), [the printable tie-out checklist](website/resources/tie-out-checklist.html), [the complete synthetic review](website/sample-review.html), [the private pilot inquiry page](website/pilot.html) and [the website](website/index.html).

## Repository history

The root-level `app.py`, `validator/` and `examples/acceptance_*` files are retained as historical work from an earlier product direction. They are not part of the current financial reconciliation workflow and must not be used in DealTie sales claims.
