# DealTie — Product and engineering status

## Product definition

DealTie is a transaction consistency control system for M&A teams. It compares analyst-confirmed financial observations across transaction documents, preserves their source references, and identifies downstream references that may need review after a version change.

## Current architecture

- **Core engine:** Python. Decimal-based deterministic reconciliation and version-change impact analysis.
- **Analyst application:** Streamlit. Document extraction, analyst confirmation, evidence ledger, reconciliation and export.
- **Public product website:** static HTML, CSS and JavaScript. Marketing, product education, interactive synthetic case and a local CSV workbench.
- **Private enquiry delivery:** Cloudflare Pages Function using Resend. Requires encrypted environment variables and a live delivery test.

## Version-change analysis

The `dealtie.change_impact.analyze_version_impact` function accepts analyst-confirmed observations with:

`document_family, version, document, metric, period, value, unit, source_ref`

It compares two versions of a source document family. For an exact metric and period match, it identifies other supplied document references whose values:
- still match the baseline version (`STALE_CANDIDATE`);
- match the current version (`ALIGNED_TO_CURRENT`);
- match neither (`OTHER_VALUE`);
- cannot be compared because the value or unit is incomplete (`INSUFFICIENT_EVIDENCE`).

The algorithm does not infer semantic equivalence, currency conversion, scale conversion, period equivalence, source authority or correctness. A stale candidate is a review lead, not proof that the downstream document is wrong.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS / Linux: source .venv/bin/activate
python -m pip install -r dealtie/requirements.txt
PYTHONPATH=. python -m unittest discover -s dealtie/tests -v
python -m compileall -q dealtie
streamlit run dealtie/app.py
```

## Current limitations

- The browser workbench accepts structured CSV only and runs locally in the browser.
- Streamlit extraction reads selectable PDF text and spreadsheet cell values. It does not perform scanned-PDF OCR, formula evaluation, semantic mapping or accounting interpretation.
- The public site and current application are not a secure multi-tenant deal room.
- Authentication, tenant isolation, role-based access, encrypted client-file storage, retention controls, immutable audit history, multi-user adjudication, production monitoring and disaster recovery are not yet implemented.
- The private enquiry form is not operational until the Cloudflare secrets are configured and a delivery test succeeds.
- Synthetic cases are illustrations, not customer results.

## Release gate

Do not describe DealTie as production-ready for confidential transaction packs until the security, access-control, storage, retention, auditability, testing, operational monitoring and professional review requirements have been implemented and independently checked.
