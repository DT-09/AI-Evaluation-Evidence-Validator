# Paid pilot scope and value measurement

## Offer

**Buyer-owned AI support acceptance evidence review**

A fixed-scope review of buyer-supplied test cases and structured run exports. The workbench applies the buyer-approved protocol, records explicit outcomes and compares the candidate run with the agreed baseline.

This is not live vendor testing, integration validation, production monitoring, a safety certification or a regulatory compliance opinion.

## Initial scope

- One customer-support workflow: ticket classification and routing.
- One buyer-approved acceptance protocol.
- Up to 50 buyer-provided test cases.
- Up to two structured system runs: two candidate suppliers, or an accepted baseline and a candidate change.
- Deterministic checks for agreed structured fields and routing outcomes.
- Human-review decisions supplied or approved by the buyer for subjective criteria.
- One case-level comparison.
- One JSON evidence package and one readable HTML report.
- One review meeting to explain results, limitations and unresolved evidence.

Out-of-scope work requires a separate written scope.

## Buyer responsibilities

The buyer or its authorised technical team must:
- execute the system tests in its approved environment;
- export the structured outputs for each test case;
- provide expected outcomes and the approved protocol;
- identify system, model, prompt, workflow and configuration versions where available;
- provide human-review decisions for subjective criteria;
- approve the data-handling and access route before any data is shared.

The current application does not execute tests against live supplier systems and has no production connectors. It cannot validate actual backend state, integration latency or live traffic.

## Deliverables

1. Acceptance protocol with stable ID and version.
2. Input/schema and coverage review.
3. Case-level PASS / FAIL / INSUFFICIENT EVIDENCE outcomes.
4. Criterion-level pass rates and hard-gate results.
5. Baseline-versus-candidate regression and resolution register.
6. Human-review record and missing-evidence register.
7. JSON evidence export and HTML report.
8. Limitations and buyer decision handoff.

## Completion criteria

The pilot is complete when:
- agreed inputs are received and validated;
- each applicable case/criterion pair has a visible outcome or explicit missing-evidence status;
- all decision rules are disclosed;
- baseline/candidate differences are traceable;
- the evidence package is delivered;
- the buyer has had the review meeting.

The buyer retains the acceptance and deployment decision.

## Value measurement

Capture the buyer's current baseline before work begins. Measure only values the buyer can substantiate.

| Measure | Baseline | Pilot result |
|---|---|---|
| Staff hours spent assembling evidence | Buyer-provided | Timed/recorded |
| Time from run completion to approval-ready evidence | Buyer-provided | Timed/recorded |
| Cases with complete expected/observed evidence | Buyer-provided | Calculated from supplied files |
| Critical failures visible before decision | Prior process record | Pilot findings |
| Missing evidence and unresolved cases | Prior process record | Pilot findings |
| Manual handoffs needed to complete review | Buyer-provided | Recorded |

Do not convert a detected discrepancy into financial savings unless the buyer confirms the financial impact and the counterfactual.

## Commercial terms

- Paid fixed-scope engagement.
- Fee and delivery schedule agreed privately after a non-confidential schema review.
- No free proof of concept.
- No public price or savings claims.
- Scope changes require written agreement.

An appropriately authorised adult/business representative must handle contracting, invoicing, payment, tax, confidentiality and data-processing arrangements.

## Data and security gate

Do not accept personal, customer, confidential or regulated data until the authorised representative has approved:
- lawful permission and purpose;
- data minimisation and redaction;
- secure transfer and access controls;
- encryption and storage location;
- retention and deletion schedule;
- logging, backups and incident process;
- confidentiality and contractual terms.

Use synthetic or non-confidential schemas for initial scoping.

## Subscription trigger

Offer a subscription only if the pilot reveals a recurring workflow and the buyer identifies:
- a predictable re-test trigger;
- a recurring owner and budget;
- a need to preserve protocol and evidence history;
- a reason the current stack is insufficient.

A second paid engagement or explicit renewal commitment is required before describing the model as repeatable.
