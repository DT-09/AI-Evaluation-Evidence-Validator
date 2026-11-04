# Product direction — DealTie Financial Evidence Reconciliation

## Product definition

DealTie is a source-linked, analyst-confirmed pre-issue financial tie-out workbench for boutique M&A advisory and financial diligence teams.

It compares selected financial observations across a transaction document pack—initially a CIM, QoE report and valuation model—and produces an inspectable exception register. It is deliberately narrower than a data room, financial model, accounting platform or diligence engagement.

## Buyer and job to be done

**Initial buyer hypothesis:** a partner, director or senior associate at a boutique M&A advisory or financial diligence firm.

**Operational user:** analyst or associate preparing or reviewing transaction materials.

**Job:** before a pack is circulated or relied upon, verify that agreed headline metrics are consistent across the relevant documents and make every unresolved difference easy to trace back to its source.

The buyer is not purchasing a generic dashboard. The useful output is a review-ready tie-out package that reduces manual cross-document checking and makes unresolved questions explicit.

This is a hypothesis, not validated demand. The repository contains no paying-customer evidence.

## Initial paid service

One scoped review:
- One authorised, non-confidential or appropriately redacted document pack.
- Up to 15 agreed headline metrics.
- Up to three source documents: CIM, QoE and valuation model.
- One agreed period map and stated unit convention.
- Source references at PDF page or Excel sheet/cell level where extractable.
- Confirmed observation ledger.
- Exception register with reported values, sources, spread, unit/period issue and open question.
- Tied / mismatch / insufficient-evidence status.
- One reviewer walkthrough and one correction pass.

Fee and delivery timing are agreed after non-confidential scoping. No public price, turnaround guarantee or savings claim is made.

## Product workflow

1. **Ingest:** read selectable PDF text, Excel cell values and structured CSV.
2. **Confirm:** analyst maps extracted text to metric, period, value and unit. No extraction result becomes a financial observation without confirmation.
3. **Reconcile:** deterministic rules compare same-named metrics and periods, applying an explicit tolerance and surfacing unit, missing-value, duplicate-source and coverage issues.
4. **Investigate:** reviewer opens each finding and inspects the original source reference and recorded values.
5. **Deliver:** export a machine-readable evidence register and a readable HTML review report.

## Product boundaries

DealTie does not:
- decide which source is authoritative;
- infer that two differently named metrics are equivalent;
- convert currencies, scales or periods;
- audit or evaluate workbook formulas;
- interpret accounting adjustments or QoE classifications;
- establish that a discrepancy is an error, misstatement, loss or recoverable amount;
- provide an audit opinion, QoE conclusion, valuation opinion, legal opinion or transaction recommendation.

Scanned-PDF OCR, semantic matching, secure deal-room hosting, authentication, role permissions, multi-user adjudication and audit-grade history are not implemented.

## Commercial validation

The immediate objective is not to build a broad SaaS platform. It is to validate whether a narrow, source-linked tie-out is painful enough that a boutique team will pay for a defined review.

Evidence required:
1. Five conversations with actual boutique advisory or diligence practitioners.
2. At least three independently describe the same recurring cross-document tie-out problem.
3. At least two share a non-confidential sample schema or synthetic example.
4. At least one qualified buyer agrees to a paid, clearly scoped pilot through an authorised adult/business representative.
5. A second paid engagement or explicit repeat-review trigger before describing revenue as repeatable.

Stop or change direction if buyers already solve the workflow adequately, require full semantic extraction or secure hosted deal rooms from day one, or do not assign budget to the review.

## Trust and data handling

The current application is a prototype, not a secure transaction environment. Use synthetic or properly redacted, authorised data only. Do not accept confidential deal files until an appropriately authorised business representative has approved written terms and suitable security, access, retention and deletion controls. Qualified finance professionals must supervise substantive financial interpretation.

## Claims policy

Do not claim customers, revenue, savings, recovered value, accuracy rates, integrations, audit readiness or production security without evidence. Synthetic examples must remain labelled synthetic. Findings are exceptions for human investigation, not financial conclusions.

## Historical repository material

Earlier AI Acceptance Assurance work is retained in root-level legacy files. It is not the current DealTie product direction. See the repository README for the boundary.
