# DealTie — Financial Evidence Reconciliation

DealTie is an analyst workbench for reconciling selected financial observations across a Confidential Information Memorandum (CIM), Quality of Earnings (QoE) report and valuation model. It flags value differences, unit conflicts, missing values and incomplete source coverage while preserving page, sheet or cell references.

## Run the DealTie prototype

From the repository root:

```bash
pip install -r dealtie/requirements.txt
streamlit run dealtie/app.py
```

Full workflow, CSV schema and limitations: [dealtie/README.md](dealtie/README.md).

## Public product page

The static product page is in [website/](website/index.html). It includes an interactive synthetic exception register. The page is not a live hosted application.

## What is implemented

- Selectable-text PDF extraction with page and line references.
- Excel workbook cell extraction with sheet and cell references.
- Structured CSV import.
- Analyst-confirmed mapping of metric, period, value and unit.
- Deterministic value, unit, missing-value and source-coverage checks.
- Source-linked findings and JSON evidence-register export.
- Automated unit tests and a GitHub Actions workflow.

## What is not implemented

- OCR for scanned PDFs.
- Semantic metric matching or automatic accounting interpretation.
- Formula auditing, currency conversion or accounting judgement.
- Secure deal-room hosting, authentication, role-based access, audit-grade history or multi-user review.
- Production readiness for confidential transaction data.

A mismatch is an investigation lead, not proof of an error or financial loss. DealTie is not an audit opinion, QoE conclusion, valuation opinion, legal opinion or transaction recommendation.

## Repository note

The original AI acceptance-assurance prototype remains in the legacy root-level files and directories on this branch. The DealTie financial reconciliation application is isolated under `dealtie/` so that the older code is not silently overwritten.

## Commercial status

No paying customer or validated willingness to pay is claimed. Any paid engagement, contracting, payment or confidential-data arrangement requires an appropriately authorised adult/business representative. Initial product discussions must use non-confidential information only.
