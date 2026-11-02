# Buyer evidence update — 2 November 2026

## Decision

The customer-support AI market has a real evaluation and deployment problem. The current evidence does **not** establish demand for a standalone buyer-side acceptance workbench. The product must be sold narrowly as a structured acceptance-evidence review of buyer-supplied test runs unless and until customers validate a broader need.

## Strongest buyer evidence

### G2's 2026 customer-experience agent evaluation

G2 reports that it evaluated nine live AI support agents in a common simulated environment, with 50 scenarios per agent and 1,950 assigned conversations. Overall scores ranged from 34% to 97%, and accuracy from 73% to 96%. It also reports more than 20 buyer interviews conducted from July to September 2026.

The report identifies recurring operational failures: acting before checking customer records, unnecessary escalation, and taking the wrong action while reporting success. It describes buyers wanting systems tested against their own policies, integrations, approval rules and cost models. One buyer described rejecting a vendor because of a slow Salesforce sync and rejecting another because of a high integration quote. Another described running two agents side by side on a small share of traffic for three to six months.

G2 also reports that 73% of surveyed buyers trust open research or independent test labs most, compared with 11% for vendor-published tests. This is evidence of demand for independent evidence, not evidence that buyers will purchase this workbench.

Source: https://ai-dev.g2.com/evaluations/insights/customer-experience

### Existing platforms already cover much of the technical workflow

Arize's 2026 platform comparison documents datasets, evaluator authoring, human review, offline and online evaluation, regression testing, monitoring, release gates, version tracking, APIs and CI/CD integration.

Source: https://arize.com/resources/llm-and-agent-evaluation-platforms/

A further direct competitor, Evalara, publicly describes release records combining baseline/candidate comparisons, critical gates, version metadata, reviewer notes, acceptance policies and approval/hold decisions.

Source: https://evalara.ai/release-loop/gate

AWS's October 2026 AgentCore evaluation guidance also describes an end-to-end lifecycle from defining quality through version comparisons, CI gates, canary testing, drift monitoring and feedback loops.

Source: https://aws.amazon.com/blogs/machine-learning/building-trust-in-ai-agents-a-production-ready-evaluation-framework-with-amazon-bedrock-agentcore/

## Updated problem hypothesis

The most defensible problem to investigate is not "AI teams lack evaluation tools." They do not.

Investigate this narrower buyer-side failure:

**The business owner cannot easily assemble a consistent, buyer-owned acceptance record across suppliers or material releases, using the same business criteria, reviewer decisions and evidence references, without depending on each supplier's own reporting interface.**

Potential recurring triggers:
- supplier selection or renewal;
- a model, prompt, workflow or configuration change;
- a material policy or integration change;
- a quality incident requiring re-acceptance;
- a move from pilot to wider deployment.

The buyer must confirm that this record is missing, costly to assemble, and not already handled by their existing evaluation stack or procurement process.

## Critical product boundary

The current application:
- imports buyer-provided case CSVs and structured run-output CSVs;
- applies explicit deterministic checks and human-review decisions;
- compares a candidate run with a baseline;
- exports a JSON and HTML evidence summary.

The current application does **not**:
- execute tests against a live third-party AI agent;
- connect to Salesforce, Zendesk, Genesys or other production systems;
- verify integration latency or actual backend state;
- monitor production traffic or drift;
- independently establish that buyer test cases are representative;
- certify safety, security, fairness or regulatory compliance.

Therefore, the first paid offer must say that the buyer or its authorised technical team supplies the test runs and exports. Any hands-on execution or integration test is a separate scope and cannot be implied by the current software.

## Commercial implication

Do not market this as an independent AI testing lab or a replacement for Arize, Braintrust, LangSmith, Langfuse, or vendor-specific evaluation tooling.

Test whether buyers will pay for:
1. translating operational requirements into a versioned acceptance protocol;
2. reviewing the completeness and structure of supplied test evidence;
3. applying transparent buyer-approved rules to exported runs;
4. recording reviewer decisions and release exceptions;
5. comparing later runs against the previously accepted record.

If buyers can already produce this package easily with their existing tools, stop or pivot. Do not build a hosted platform before the paid pilot proves repeated use.

## Named discovery prospects

See [commercial/prospect-pipeline.md](../commercial/prospect-pipeline.md). Names and roles are research leads, not confirmed buyers or completed interviews. Current role and decision authority must be reconfirmed before outreach.

## Evidence required next

- Five completed interviews with current customer-operations decision makers across independent organisations.
- Three independent buyers describing the same recurring acceptance-evidence failure.
- Two buyers willing to share a non-confidential protocol/schema or synthetic example.
- One qualified buyer willing to scope a paid pilot through an authorised contracting route.
- One repeat review trigger or second paid engagement before treating subscription demand as credible.
