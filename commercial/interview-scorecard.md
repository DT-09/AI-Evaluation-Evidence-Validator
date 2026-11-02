# Buyer interview guide and evidence scorecard

## Purpose

Test whether buyer-owned acceptance evidence across third-party AI support suppliers and system changes is a recurring, costly problem that existing tools do not adequately solve.

Do not demonstrate the product at the start. Reconstruct the buyer's last real decision.

## Opening

"We are researching how customer-operations teams evaluate and re-approve AI-enabled support workflows when they select a supplier or a system changes. I am not assuming your process has a gap. I would like to understand the last real evaluation or change you handled."

Ask permission to take notes. Do not ask for confidential information.

## Interview questions

### A. Recent event and decision owner
1. What was the most recent AI-enabled support system you evaluated, deployed or materially changed?
2. What workflow did it perform: classification, routing, knowledge answers, case resolution, voice, or another task?
3. What decision were you making, and who had final approval?
4. Which supplier, model, configuration or workflow versions were involved?

### B. Acceptance process
5. How did you define acceptable performance before approval?
6. Who created the test cases and expected outcomes?
7. Did the supplier provide its own evaluation results? What did your team independently verify?
8. How did you test policy compliance, escalation, permissions, integrations and actual task outcomes?
9. What evidence was retained, and where?

### C. Change and failure
10. What happened the last time the model, prompt, workflow, integration or policy changed?
11. Did you re-run the same cases? If not, why not?
12. How did you identify regressions against the previously accepted version?
13. Describe one failure that was difficult to detect before it affected operations.
14. What was the consequence: rework, delay, customer impact, cost, risk or a blocked launch? Use only figures the buyer can substantiate.

### D. Existing tools and gap
15. Which products, internal QA processes, spreadsheets, dashboards or consultants already support this work?
16. What does each tool do well?
17. What still requires manual effort or falls between teams?
18. Could your current stack produce a buyer-owned, versioned acceptance record across suppliers and releases? If not, what exactly is missing?
19. Would a new tool duplicate an existing platform capability?

### E. Recurrence and willingness to pay
20. How often does this review happen?
21. What triggers the next review?
22. Who owns the budget for acceptance testing or change assurance?
23. Have you paid an external party for similar work?
24. What would a useful paid review need to deliver?
25. Would you consider a scoped paid pilot? What procurement and security steps would apply?

## Evidence scorecard

Score each category 0–2. Record the buyer's exact evidence separately from the interviewer's interpretation.

| Category | 0 | 1 | 2 |
|---|---|---|---|
| Decision ownership | No authority or access | Influences decision | Owns or co-owns acceptance |
| Recent trigger | No real example | Older or indirect example | Recent, specific evaluation/change |
| Recurring failure | No gap | General dissatisfaction | Specific repeatable failure |
| Existing-tool gap | Current process adequate | Some manual workaround | Material unresolved gap |
| Recurrence | One-off | Occasional | Regular or trigger-based repeat |
| Evidence access | No export/schema access | Possible with approval | Non-confidential sample/schema available |
| Budget | No owner | Owner unclear | Identified budget owner |
| Paid intent | No interest | General interest | Will scope paid work |

Maximum: 16. A high score does not replace the qualification gates below.

## Qualification gates

A prospect counts as a qualified discovery interview only if they have:
- direct responsibility or material influence over the workflow;
- a recent concrete evaluation or system change;
- a specific gap not adequately solved by existing tools;
- a recurring trigger or upcoming decision;
- a plausible route to approved sample/schema access;
- an identifiable budget owner.

A buyer counts as paid-pilot qualified only when they agree to discuss a paid, bounded scope with an authorised contracting route.

## Interview record template

- Organisation:
- Interviewee and current role:
- Date:
- Decision authority:
- System/workflow:
- Last concrete evaluation/change:
- Acceptance criteria used:
- Existing tools/process:
- Specific failure and evidence:
- Time/cost/risk consequence:
- Frequency/next trigger:
- Data/export availability:
- Budget owner:
- Score / 16:
- Qualification: yes/no and reason:
- Agreed next step:
- Direct buyer statements:
- Interviewer interpretation:

## Stop conditions

Do not force the product into the conversation. If the buyer already has a clean process, say so in the record. If the issue is integration testing, live monitoring or semantic evaluation, do not pretend the current CSV workbench solves it. Record the requirement as a product gap or disqualifier.
