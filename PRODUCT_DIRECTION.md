# DealTie — Transaction Consistency Control

## Product

DealTie compares analyst-confirmed financial observations across M&A transaction documents and successive versions. It preserves source references and identifies downstream observations that may require human review after a source figure changes.

Initial workflows: selected CIM, Quality of Earnings (QoE), valuation-model and management-presentation metrics. Initial buyer hypothesis: boutique M&A advisory, transaction advisory and financial diligence teams. Demand and willingness to pay remain unvalidated.

## Implemented engine

- Python deterministic reconciliation using explicit Decimal tolerance.
- Value, unit, duplicate-source, missing-data and coverage exceptions.
- Source-linked evidence ledger and JSON/CSV/HTML report outputs.
- Version-change analysis in `dealtie.change_impact.analyze_version_impact`.
- Streamlit multipage interface, including the Version Impact page.

The version-impact function accepts `document_family,version,document,metric,period,value,unit,source_ref`. It compares two selected versions of a source family and classifies exact downstream metric-period matches as `STALE_CANDIDATE`, `ALIGNED_TO_CURRENT`, `OTHER_VALUE` or `INSUFFICIENT_EVIDENCE`.

It does not infer semantic equivalence, currency/scale/period conversion, source authority or correctness. A stale candidate is a review lead, not proof of an error.

## Application and website

- Core: Python and Decimal arithmetic.
- Analyst application: Streamlit.
- Public site and local CSV workbench: HTML, CSS and JavaScript.
- Public site deployment target: Cloudflare Pages.
- Analyst application deployment target: Streamlit Community Cloud.

## Limitations

Scanned-PDF OCR, semantic metric mapping, formula evaluation, secure deal-room hosting, authentication, tenant isolation, role permissions, encrypted client-file storage, immutable audit history, multi-user adjudication, production monitoring and disaster recovery are not implemented.

Use synthetic or properly redacted and authorised data only. Do not upload confidential transaction material to the current prototype. Qualified finance professionals must supervise substantive interpretation.

## Commercial validation

The target is a recurring cross-document tie-out and version-change workflow. A paid scoped review is an offer to validate demand, not proof of repeatable revenue. No customers, revenue, savings, accuracy rates or willingness-to-pay evidence are claimed.

Do not describe DealTie as production-ready for confidential transaction packs until security, access control, storage, retention, auditability, operational monitoring, backup/recovery and independent review are implemented and verified.
