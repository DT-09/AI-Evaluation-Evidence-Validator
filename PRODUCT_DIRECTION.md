# Product direction: Buyer-side AI Acceptance Assurance

**Working product thesis:** a vendor-neutral acceptance and change-control evidence system for organisations buying or operating third-party AI systems.

## The buyer's decision

Can this AI system meet our defined business requirements today, and can we prove that a supplier/model/prompt/configuration change has not broken those requirements?

The buyer—not the AI vendor—owns the acceptance protocol, criticality, thresholds, evidence and final decision.

## Initial customer wedge

**Initial segment hypothesis:** operations and procurement teams evaluating third-party customer-support automation systems.

This is a hypothesis, not a validated beachhead. Do not expand to all AI use cases until buyer interviews show that the same workflow and acceptance criteria recur.

### Economic buyer / users

- Economic buyer: Head of Customer Operations, COO, or procurement owner sponsoring an AI automation purchase.
- Operational owner: customer-support operations or quality lead.
- Technical contributor: AI/platform or vendor engineering team.
- Risk reviewer: privacy, security, legal or compliance staff where relevant.

## Product workflow

1. **Define acceptance:** buyer creates a versioned protocol from real business tasks, expected outcomes, severity levels, thresholds and evidence requirements.
2. **Test candidates:** run the same buyer-owned cases against each candidate vendor or system version. Initial ingestion supports structured run exports; live connectors are not assumed.
3. **Review exceptions:** deterministic checks identify objective failures; human reviewers adjudicate subjective or high-impact cases with rationale.
4. **Decide:** the system applies pre-agreed hard gates and thresholds. It reports PASS / FAIL / INSUFFICIENT EVIDENCE; it does not make an unqualified safety or compliance certification.
5. **Control changes:** compare a proposed vendor/model/prompt/configuration version with the accepted baseline. Show new failures, resolved failures, changed outcomes and evidence coverage.
6. **Preserve evidence:** generate a buyer-owned, versioned acceptance record with test-set version, system version, run metadata, evaluator versions, reviewer decisions, exclusions and hashes.

## Why this is not another evaluation platform

Existing evaluation platforms already provide many core engineering capabilities: datasets, evaluators, traces, offline experiments, regression tests, production evaluation, human review and release gates. We must not claim these are missing.

The intended product boundary is the **buyer-side procurement and supplier-change control record**:
- one acceptance protocol that remains buyer-owned across competing suppliers;
- explicit mapping from business requirements to test cases and acceptance decisions;
- a controlled record of what was accepted, by whom, against which version and evidence;
- repeatable re-acceptance when a supplier changes a model, prompt, workflow or configuration;
- exportable evidence for procurement, operations and risk review without forcing the buyer to adopt one vendor's engineering stack.

This is a positioning and workflow hypothesis. Existing platforms may be configurable to do much of it. The product only deserves to exist if buyers confirm that the cross-vendor acceptance and change-control workflow is materially painful and inadequately served.

## Competitive facts and boundaries

- Arize's 2026 comparison describes leading evaluation platforms as supporting datasets, evaluators, experiments, regression testing, production evaluation, human review, dashboards, release gates and version tracking: https://arize.com/resources/llm-and-agent-evaluation-platforms/
- PwC publicly offers broad AI and technology diligence, including AI maturity, product/platform assessments, roadmap realism, value diagnostics and data/compliance risk review: https://www.pwc.com/us/en/services/consulting/deals/strategy-value-creation/ai-technology-diligence.html
- Brookings has argued that access alone does not establish independent evidence and highlights the need to disclose methodology, access, funding and publication control: https://www.brookings.edu/articles/in-ai-evaluation-access-is-not-evidence/

These sources support the existence of an active evaluation/diligence ecosystem and the importance of evidence quality. They do **not** prove demand for this product or prove that competitors cannot perform the workflow.

## Defensibility hypothesis

The potential moat is not a dashboard or a collection of metrics. It is the accumulation of:
- buyer-owned, versioned acceptance protocols for a specific operational domain;
- carefully curated edge-case and failure taxonomies;
- historical acceptance/change records across vendors and releases;
- validated evaluator/rubric calibration and adjudication procedures;
- integrations into procurement, change approval and operational quality workflows.

No proprietary benchmark or network effect exists yet. These are assets to earn through repeated customer use, not claims to make today.

## Commercial model hypothesis

- Paid initial acceptance assessment for one workflow and one or more candidate systems.
- Annual or monthly subscription for maintaining protocols, re-testing vendor changes and retaining evidence history.
- Expansion by additional workflows, business units and suppliers.

Pricing, willingness to pay and renewal frequency are unvalidated. Do not publish invented prices or savings.

## Kill criteria

Stop or materially change direction if buyer discovery shows any of the following:
1. Target buyers already solve the workflow adequately with their current evaluation platform, spreadsheets and procurement process.
2. Supplier access or export restrictions make repeatable testing impractical.
3. The buyer has no budget owner or no recurring trigger to re-run acceptance.
4. The workflow is too bespoke to standardise across customers.
5. A specialist consultancy already provides the required outcome at a price buyers prefer, with no demand for software.

## Evidence required before claiming product-market fit

- At least 5 interviews with actual buyers/users in the target segment.
- At least 3 independently describe the same costly workflow failure.
- At least 2 agree to provide a non-confidential sample protocol or synthetic schema for workflow design.
- At least 1 qualified buyer agrees to a paid pilot with a defined scope and authorised contracting.
- A second paid engagement or explicit recurring re-test requirement before describing revenue as repeatable.

## Claims policy

Never claim certification, compliance, safety assurance, benchmark validity, independent verification, customer outcomes, accuracy, savings or integrations unless the specific claim is demonstrably supported. The product records evidence and applies stated acceptance rules; the responsible buyer makes the acceptance decision.
