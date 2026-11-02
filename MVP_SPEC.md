# MVP specification: Buyer-side AI Acceptance Assurance

## Product objective

Enable a buyer to define acceptance requirements once, test multiple AI supplier/system versions against the same protocol, adjudicate failures, and retain a defensible change record.

The MVP is not a generic LLM evaluation platform, an observability suite, an AI audit, or a certification product.

## Initial workflow boundary

Customer-support automation for one defined workflow, such as classifying and routing incoming support requests. Do not initially support every customer-service task or every AI modality.

## Core objects

### 1. Acceptance protocol
- Protocol ID and version
- Buyer/workflow name
- Intended use and out-of-scope cases
- Acceptance criteria with stable IDs
- Criterion type: deterministic / human rubric
- Severity: critical / major / minor
- Threshold and hard-gate rules
- Required evidence fields
- Approval owner and effective date

### 2. Test case
- Stable case ID and version
- Input payload
- Expected outcome or reviewer rubric
- Criterion IDs covered
- Severity and scenario category
- Source/author and approval status
- Sensitive-data classification (metadata only; do not store real sensitive data in an unreviewed deployment)

### 3. System submission
- Supplier/system name
- Model, prompt, workflow and configuration version where disclosed
- Run ID and timestamp
- Protocol version
- Structured output for each test case
- Evidence references and source hashes

### 4. Review decision
- Case and criterion IDs
- Deterministic result or reviewer outcome
- Reviewer identity/role
- Rationale and timestamp
- Adjudication state: accepted / failed / inconclusive
- Conflict and escalation status

### 5. Acceptance decision
- PASS / FAIL / INSUFFICIENT EVIDENCE
- Hard-gate results
- Threshold results
- Coverage and missing evidence
- Approver and decision timestamp
- Protocol and system versions
- Explicit limitations

## Required product capabilities

### A. Protocol authoring
Create, edit and version acceptance protocols. A new version must not silently rewrite prior decisions.

### B. Case-set management
Import structured test cases; validate schema; preserve stable IDs and versions; identify missing/duplicate IDs; show coverage by criterion and severity.

### C. Cross-system run ingestion
Import structured outputs from multiple candidate systems against the same protocol. Record system/version metadata and file hashes. No proprietary vendor API integration is assumed for MVP.

### D. Deterministic checks
Support only explicit, testable checks in the first release:
- exact value / allowed-value checks;
- required-field and JSON-schema checks;
- routing/classification outcome checks;
- threshold and hard-gate evaluation;
- missing/duplicate case detection;
- run completeness and protocol-version matching.

Do not infer semantic correctness from a deterministic check.

### E. Human adjudication
Provide a review queue for subjective criteria. Capture reviewer outcome, rationale, timestamp and disagreement. Do not silently substitute an LLM judge for human ground truth.

### F. Change comparison
Compare a candidate run to an accepted baseline using stable case IDs and protocol versions. Show:
- newly failed cases;
- previously failed cases now passing;
- unchanged outcomes;
- missing or uncomparable cases;
- changes in aggregate criterion outcomes;
- changes to system metadata.

### G. Evidence record
Generate a machine-readable JSON package and readable HTML/PDF report containing:
- protocol and case-set versions;
- supplier/system/run metadata;
- source hashes;
- evaluator/check versions;
- case-level outcomes and reviewer rationale;
- acceptance rules and computed decision;
- coverage, exclusions and limitations.

## Non-functional requirements

- Local-first processing for initial private pilots.
- No third-party model API required for deterministic checks.
- No sensitive customer data accepted until access, encryption, retention, deletion, logging, backup and contractual controls are reviewed.
- Explicit role separation between author, reviewer and approver in any multi-user hosted version.
- Reproducible calculations and deterministic report generation.
- Tests for boundary conditions, missing evidence, changed protocols and incomplete runs.
- Export format must be documented and stable.

## MVP acceptance criteria

The MVP is complete only when all of the following work end-to-end on synthetic data:
1. Create and version an acceptance protocol.
2. Import a versioned case set.
3. Import two system runs against the same protocol.
4. Validate run completeness and schema.
5. Apply deterministic criteria.
6. Record human review decisions for subjective criteria.
7. Calculate PASS / FAIL / INSUFFICIENT EVIDENCE using explicit hard gates and thresholds.
8. Compare the candidate run to the accepted baseline.
9. Export a complete evidence record and human-readable report.
10. Re-run the same inputs and reproduce the same deterministic results.
11. Automated tests cover every decision rule and important failure mode.

## Explicitly out of scope for MVP

- Production tracing/observability.
- Prompt engineering or agent building.
- LLM-as-a-judge as an authoritative acceptance mechanism.
- Live integrations with every AI vendor.
- Automated legal or regulatory compliance conclusions.
- Security penetration testing or model red-teaming.
- Claims of universal AI quality or safety.
- Multi-industry benchmark library.

## Commercial validation gates

Do not build the full hosted platform until discovery confirms:
- buyers repeatedly compare or re-accept third-party AI suppliers;
- the current process creates measurable cost, delay or risk;
- the buyer owns or can access representative acceptance cases;
- a budget owner will pay for initial assessment and recurring change review.

A paid pilot must use a narrowly agreed scope and appropriately authorised adult/business contracting and data-handling arrangements.
