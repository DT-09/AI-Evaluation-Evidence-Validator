# AI Acceptance Assurance

A local-first, buyer-owned workbench for evaluating third-party AI system outputs against a versioned acceptance protocol, recording human adjudication, and comparing candidate runs with an accepted baseline.

## Product purpose

The buyer defines the acceptance criteria. The same protocol and case set can be used to evaluate competing supplier systems or later system versions. The workbench records case-level outcomes, applies explicit thresholds and hard gates, and produces a portable evidence package.

This is an acceptance-workflow aid. It is not an AI safety certification, regulatory compliance opinion, general AI audit, or production observability platform.

## Run locally

Python 3.10 or newer is recommended.

```bash
git clone https://github.com/DT-09/AI-Evaluation-Evidence-Validator.git
cd AI-Evaluation-Evidence-Validator
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The application processes uploaded files in the running app session. It does not require a third-party model API.

## Input contract

### Acceptance protocol JSON

See `examples/acceptance_protocol.json`.

A protocol defines:
- protocol ID and version;
- workflow and case-set version;
- criteria, criterion types, severity and minimum pass rates;
- overall pass-rate and case-coverage thresholds;
- severities that trigger a hard failure.

Supported criterion types:
- `exact_match`: compare an output field with a buyer-defined expected field;
- `allowed_values`: require an output field to belong to a fixed allowed set;
- `required_field`: require an output field to be present and non-empty;
- `regex_match`: require an output field to match a buyer-defined regular expression;
- `human_review`: require a separate reviewer decision.

### Test case CSV

Required columns:
- `case_id`: stable, unique test-case identifier;
- `expected_json`: JSON object containing expected values;
- `criterion_ids`: semicolon-separated criterion IDs that apply to the case.

Additional context columns such as `input_text` may be included.

### System run CSV

Required columns:
- `case_id`: test-case identifier;
- `output_json`: JSON object emitted by the candidate system.

### Human-review CSV

Required columns:
- `case_id`;
- `criterion_id`;
- `decision`: `PASS`, `FAIL`, or `INCONCLUSIVE`.

Optional columns include `rationale` and `reviewer_id`.

## Decision semantics

- **PASS** — the supplied run met the stated protocol and evidence-coverage rules.
- **FAIL** — a hard-gate failure or an explicit threshold was not met.
- **INSUFFICIENT EVIDENCE** — case coverage, human review or other required evidence is incomplete.

A PASS is not a general claim that an AI system is correct, safe, fair, compliant or suitable for every use.

## Change comparison

When an accepted baseline run is supplied, the workbench compares case/criterion statuses and reports regressions, resolved failures and other changes. Comparisons are meaningful only when the protocol and case-set versions are compatible.

## Evidence package

The JSON and HTML exports include protocol identifiers and versions, run metadata, source-file SHA-256 hashes, criterion outcomes, case-level details, decision rules and limitations.

## Synthetic examples

The `examples/` directory contains a synthetic customer-support routing protocol, case set, baseline run, candidate run and human-review file. These are test fixtures, not customer results or performance claims.

## Current boundaries

- Local-first single-user workflow; no hosted multi-tenant service or authentication.
- Structured CSV/JSON imports; no live vendor connectors.
- Initial scope is a small set of explicit deterministic checks plus human review.
- No automatic proof that test cases are representative or complete.
- No semantic correctness guarantee from deterministic checks.
- No automatic safety, security, fairness or regulatory determination.
- No customer validation or proven willingness to pay yet.

## Data handling

Do not upload personal, confidential or transaction-sensitive data to an unreviewed deployment. Before any real customer engagement, access, encryption, retention, deletion, logging, backups and confidentiality terms must be reviewed and approved. Contracting, payment and data arrangements require an appropriately authorised adult/business representative.

## Tests

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py validator tests
```

## Product strategy

See:
- [Product direction](PRODUCT_DIRECTION.md)
- [MVP specification](MVP_SPEC.md)
- [Competitive workflow review](research/COMPETITIVE-WORKFLOW-REVIEW.md)

The buyer-side acceptance and change-control workflow is a commercial hypothesis. It must be validated with actual buyers before the product is expanded or marketed as differentiated.
