# Competitive workflow review — 2 November 2026

## Decision

Do not compete as another general-purpose AI evaluation platform. Test a narrower buyer-side product: acceptance protocols and change-control evidence for third-party AI suppliers.

## What existing platforms already cover

Arize's published 2026 comparison describes the category as including:
- datasets and versioned test cases;
- deterministic, embedding-based, custom and LLM-based evaluators;
- offline experiments and regression testing;
- production/online evaluation;
- human review and annotation;
- dashboards, monitors, alerts and release gates;
- APIs, SDKs and CI/CD integration;
- model, prompt, application, evaluator and dataset version tracking.

Source: https://arize.com/resources/llm-and-agent-evaluation-platforms/

Implication: metrics, test datasets, regression comparisons, evidence exports and evaluator traceability are not differentiators by themselves.

## What diligence providers already cover

PwC publicly describes AI and technology diligence that includes AI maturity benchmarking, operating model assessment, product/platform review, roadmap realism, value diagnostics, and data/compliance risk diagnostics.

Source: https://www.pwc.com/us/en/services/consulting/deals/strategy-value-creation/ai-technology-diligence.html

Implication: broad AI diligence is not an attractive claim for a small new product. A narrowly repeatable buyer workflow may be more addressable, but this remains to be validated.

## Evidence-quality issue

Brookings' article, "In AI evaluation, access is not evidence", argues that external access alone does not establish independent evidence. It highlights methodology, access, funding and publication control as relevant factors.

Source: https://www.brookings.edu/articles/in-ai-evaluation-access-is-not-evidence/

Implication: provenance and independence matter, but merely recording sources or hashes does not create independent validation.

## Proposed wedge to validate

Buyer-owned AI supplier acceptance and change control:
- one acceptance protocol can be applied across candidate suppliers;
- criteria and case sets are controlled by the buyer;
- system/version changes are compared against the accepted baseline;
- exceptions require explicit human adjudication;
- the acceptance decision is traceable to criteria, test cases, system version and evidence;
- the buyer retains a portable evidence record independent of the supplier's evaluation UI.

## What remains unproven

- Whether target buyers actually lack this workflow.
- Whether existing platforms plus internal spreadsheets already solve it.
- Whether buyers can obtain enough structured supplier outputs.
- Whether the pain recurs often enough for subscription revenue.
- Whether a buyer has budget for a standalone tool.
- Whether this can be standardised within a single vertical.

## Next validation actions

1. Interview five customer-operations/procurement buyers who have evaluated or deployed third-party AI support systems.
2. Ask them to reconstruct their last supplier selection or material system change.
3. Request a non-confidential description of acceptance criteria, evidence received, approval steps, time spent and failure consequences.
4. Ask what tool/process owns each step and where it breaks.
5. Only build features tied to repeated, specific workflow failures.
6. Seek one paid pilot before building broad integrations or a hosted multi-tenant platform.

## Source caveats

The Arize comparison is vendor-authored and includes Arize products; it is useful for documented category capabilities, not independent market-share claims. PwC's page establishes the scope of its own service offering, not market-wide demand. The Brookings article is conceptual evidence-quality analysis, not proof of willingness to pay for this product.
