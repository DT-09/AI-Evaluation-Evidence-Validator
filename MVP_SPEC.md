# MVP specification — DealTie Financial Evidence Reconciliation

## Objective

Produce a reproducible, source-linked exception register for analyst-confirmed financial observations across a small transaction document pack.

## User and initial use case

An analyst at a boutique M&A advisory or financial diligence firm checks selected headline figures across a CIM, QoE report and valuation model before circulation or review.

## Core observation

Each observation contains:
- document label;
- metric;
- period;
- reported value;
- stated unit;
- source reference (PDF page, worksheet/cell or supplied reference).

The analyst must confirm financial meaning. Extracted text is not a confirmed observation.

## Required capabilities

### Source intake
- Selectable-text PDF extraction with page references.
- Excel/XLSX cell extraction with sheet and cell references.
- Structured CSV import.
- File-size validation and visible import errors.

### Confirmation and ledger
- Batch review of extracted candidate observations.
- Manual observation entry and removal.
- Required-field validation.
- Stable display of all confirmed observations before reconciliation.

### Deterministic comparison
- Group by normalised metric and period labels.
- Compare only explicitly stated numeric values.
- Explicit absolute tolerance.
- Surface unit conflicts without conversion.
- Surface missing/non-numeric values, duplicate source references and insufficient document coverage.
- Preserve every contributing observation in each finding.

### Review and delivery
- Findings table and per-finding source observations.
- JSON evidence-register export.
- Flat CSV observation export.
- Readable HTML review report with generated timestamp, stated tolerance, finding explanations, source trail and explicit limitations.
- Repeatable results for the same input observations and tolerance, excluding generated timestamp metadata.

## Decision rules

- `TIED`: at least two distinct documents, one consistent stated unit, complete numeric values, no duplicate source references, and spread less than or equal to tolerance.
- `VALUE_MISMATCH`: comparable complete numeric observations with the same stated unit and spread greater than tolerance.
- `UNIT_MISMATCH`: stated units differ; do not convert.
- `MISSING_OR_NON_NUMERIC`: a value, unit or source reference is missing or a value cannot be parsed.
- `DUPLICATE_SOURCE_ENTRY`: a document/source reference pair is repeated within a metric/period group.
- `INSUFFICIENT_COVERAGE`: fewer than two distinct documents are represented.

Priority order is explicit in the implementation: value and unit conflicts first; duplicate-source and missing/non-numeric evidence next; insufficient source coverage after that; tied metrics last. This is workflow triage only, not a financial materiality or risk score. A finding receives one status and a reviewer must inspect all observations before drawing a conclusion.

## Out of scope

- OCR for scanned PDFs.
- Semantic metric matching or automatic accounting interpretation.
- Formula evaluation or workbook audit.
- Currency, scale or period conversion.
- Automatic source hierarchy or authoritative-source selection.
- Secure hosted deal rooms, authentication, role-based access, encryption-at-rest, multi-user review or audit-grade history.
- Audit, QoE, valuation, legal or transaction opinions.

## MVP acceptance checks

1. Load the synthetic example.
2. Upload supported source formats and see literal extraction references.
3. Confirm selected extracted observations.
4. Add and remove manual observations.
5. Import a valid CSV and reject invalid schemas with clear errors.
6. Run comparisons with configurable non-negative tolerance.
7. Inspect all findings and their source observations.
8. Export JSON, CSV and HTML review report.
9. Verify report escaping and source traceability.
10. Run automated tests and compile the application.

## Commercial readiness gates

A working prototype is not production-ready. Before accepting confidential live deal material, implement and review authentication, authorisation, encryption, retention/deletion, secure storage, audit logging, backup and incident procedures. Contracting and payment must be handled by an appropriately authorised adult/business representative, and qualified finance professionals must supervise financial interpretation.

Before building a hosted platform, validate recurring buyer pain and willingness to pay through practitioner interviews and at least one properly authorised paid pilot.
