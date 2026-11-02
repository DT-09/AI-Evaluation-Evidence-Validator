# Independent AI Evaluation Verification Assessment

## The decision question

Can selected AI performance claims be independently reconstructed from the evaluation records supplied for review?

This is a focused evidence-verification engagement. It is not a full technical, legal, security, or investment due-diligence opinion.

## Initial paid pilot

**Scope:** One binary-classification evaluation export, one reported-metrics file, one model/evaluation configuration, and up to 25,000 records.

**Delivery target:** Five business days after complete, usable inputs are received and the scope is agreed.

**Pilot fee:** USD 250 (or local-currency equivalent) as an initial commercial test price. The final scope, payment route, tax treatment and contract must be agreed through an appropriately authorised adult/business representative.

## Client inputs

- CSV with `record_id`, `split`, `actual`, and `predicted` columns.
- Reported metric claims and their definitions.
- Positive-class definition.
- Model, dataset and evaluation-run identifiers or versions, where available.
- Relevant evaluator/configuration metadata and known exclusions.

Do not send personal data, trade secrets or confidential transaction materials until confidentiality, access, retention, deletion and contractual arrangements have been reviewed and approved.

## Deliverables

1. **Recalculated metrics:** accuracy, precision, recall, F1 and specificity, with formulas and confusion-matrix counts.
2. **Claim comparison:** reported versus recalculated values, absolute differences and the configured tolerance.
3. **Evidence integrity register:** required-field gaps, invalid labels, duplicate record IDs and exact record-ID overlap across splits.
4. **Statistical review:** 95% percentile-bootstrap intervals for supported metrics, with seed, resample count and assumptions stated.
5. **Findings report:** what matched, what differed, what could not be tested, limitations and follow-up questions.
6. **Reproducibility package:** JSON results, HTML report, source-file SHA-256 hashes, input counts, settings and calculation metadata.

## Acceptance criteria

The engagement is complete when the client receives the agreed report and machine-readable evidence package, the source-file hashes and settings are recorded, and every reported claim is labelled as matched, discrepant or not tested.

A PASS means only that the configured check found no discrepancy in the supplied evidence. It is not certification.

## Explicit exclusions

- No verification that supplied labels are correct or that exports are complete or representative.
- No proof of benchmark independence, data rights, provenance or absence of semantic/indirect leakage.
- No model-card, codebase, architecture, security, fairness, safety or production-performance audit.
- No causal, legal, accounting, valuation or investment opinion.
- No guarantee that the model performs well outside the supplied evaluation sample.

## Current technical boundary

The implemented workflow supports binary classification only. Regression, ranking and generative-AI evaluation tasks are outside the initial pilot.

## Scoping process

1. A short discovery call establishes the claim, task, data shape and decision deadline.
2. The client provides a non-confidential schema/sample first.
3. Scope, access, confidentiality, adult-authorised contracting and payment arrangements are agreed before any real client data is transferred.
4. The assessment begins only after the inputs and scope are accepted.
