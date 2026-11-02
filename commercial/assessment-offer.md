# Paid pilot: AI support workflow acceptance review

## Buyer decision

Does a third-party AI support workflow meet the buyer's defined acceptance criteria, and what changes when the supplier releases a new version?

This is a scoped operational acceptance review. It is not a general AI audit, safety certification, legal opinion or compliance attestation.

## Initial pilot boundary

- One customer-support workflow: ticket classification and routing.
- One buyer-approved acceptance protocol.
- Up to 50 buyer-provided test cases.
- Up to two system runs (for example, two suppliers or an accepted baseline and candidate release).
- Explicit deterministic checks for structured routing outcomes and required output fields.
- Human-review decisions supplied or approved by the buyer for subjective criteria.
- One case-level comparison and evidence report.

Any change to the case count, number of systems, criteria, review effort or data handling changes the scope and must be agreed before work starts.

## Buyer inputs

- Workflow description and decision context.
- Acceptance criteria and severity definitions, or a working session to draft them.
- Non-confidential or appropriately approved test cases.
- Structured outputs from each system run.
- Expected outcomes for deterministic checks.
- Human-review rubric and reviewer decisions for subjective checks.
- System/version metadata where available.

Do not transfer personal, confidential or customer data until a responsible adult/business representative has reviewed and approved the contract, permissions, access controls, retention, deletion and security arrangements. Initial scoping should use synthetic or non-confidential examples.

## Deliverables

1. Versioned acceptance protocol.
2. Case coverage and schema review.
3. Case-level PASS / FAIL / INSUFFICIENT EVIDENCE results.
4. Hard-gate and threshold summary.
5. Baseline-versus-candidate regression register.
6. Human-review record, where supplied by the buyer.
7. JSON evidence package and readable HTML report.
8. Limitations and unresolved evidence register.

## Acceptance criteria for delivery

The pilot is complete when the agreed inputs have been processed, every test case/criterion result is traceable, decision rules are disclosed, missing evidence is visible, and the buyer receives the agreed evidence package.

The tool does not decide whether a system is safe or legally compliant. The buyer retains the final procurement and deployment decision.

## Commercial terms

Paid, fixed-scope pilot. Fee and delivery timing are agreed privately after a non-confidential schema review and confirmation of scope. No free proof-of-concept and no public price claim.

Contracting, payment, tax and confidential-data arrangements must be handled by an appropriately authorised adult/business representative.

## What must be validated before scaling

- Buyers have a recurring supplier acceptance/change-control problem.
- They can obtain structured outputs from candidate systems.
- Existing evaluation platforms and internal processes do not adequately solve the buyer-owned cross-supplier workflow.
- A budget owner will pay for the pilot.
- At least one buyer wants repeat acceptance reviews after supplier changes.
