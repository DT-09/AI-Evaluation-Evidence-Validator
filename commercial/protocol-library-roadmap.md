# Workflow-specific acceptance protocol library

**Status:** proposed taxonomy. None of these protocols is customer-validated or a market benchmark.

## Design principle

Each protocol is a reusable starting structure, not a universal standard. A buyer must approve its criteria, thresholds, severity and case set before use. Do not reuse customer data or proprietary policies without explicit permission.

## Initial protocol families

| Protocol family | Workflow | Observable acceptance dimensions | Typical hard gates |
|---|---|---|---|
| Ticket classification | Assign intent/category to an incoming support request | Correct category, required fields, ambiguity handling | Critical misclassification on protected categories |
| Ticket routing | Assign queue/team/owner | Correct destination, required routing metadata, escalation path | Wrong queue for high-impact cases |
| Priority assignment | Set urgency and service level | Correct priority, response target, escalation condition | Under-prioritisation of critical cases |
| Human handoff | Transfer a case to a human | Handoff trigger, context preservation, no false claim of resolution | Missing handoff when required |
| Knowledge-grounded response | Answer from approved support material | Required source reference, policy version, unsupported-claim review | Unsupported answer on a critical policy |
| Transaction approval boundary | Recommend or prepare an action without unauthorised execution | Permission state, approval requirement, action boundary, audit record | Any prohibited action executed without required approval |

## Protocol object fields

Every protocol should record:
- protocol ID and semantic version;
- workflow and intended use;
- explicit exclusions and assumptions;
- owner and approver roles;
- criterion IDs and definitions;
- criterion type and evaluator method;
- severity and threshold;
- required evidence fields;
- test-case categories and coverage target;
- human-review rubric and adjudication process;
- system/version metadata requirements;
- effective date and change history;
- known limitations.

## Case taxonomy

A useful case set should cover:
- common routine cases;
- boundary and ambiguous inputs;
- incomplete or malformed inputs;
- policy-sensitive cases;
- escalation and human handoff;
- integration failure or stale data;
- high-impact or prohibited actions;
- previously observed production failures.

The library must not imply that its cases are representative of every buyer's workload. Buyers must validate coverage against their own traffic and risk profile.

## Calibration and governance

Before a protocol is used for a commercial acceptance decision:
1. Have the buyer approve the intended use and exclusions.
2. Map each business requirement to a testable criterion.
3. Identify where deterministic checks are appropriate.
4. Use human adjudication for subjective or high-impact criteria.
5. Test reviewer agreement on a sample.
6. Record false positives, false negatives and unresolved cases.
7. Version every change; do not rewrite prior acceptance decisions.
8. Review protocol usefulness after each real deployment/change cycle.

## Defensibility hypothesis

Potential defensibility comes from validated workflow structures, edge-case taxonomies, calibrated rubrics and accumulated change-review practice. It does not come from copying customer datasets or collecting generic templates. The library becomes an asset only after repeated buyer use and documented validation.
