# AI Evaluation Evidence Validator

A local-first application for independently recalculating reported binary-classification metrics from row-level evaluation exports and recording evidence checks.

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

The application opens in your browser. It processes the files in the running app session; it does not require a third-party model API.

## Input contract

### Evaluation CSV

Required columns:

| Column | Meaning |
|---|---|
| `record_id` | Stable identifier for an evaluated example |
| `split` | Dataset split label, e.g. train, validation, test |
| `actual` | Ground-truth binary label: 0 or 1 |
| `predicted` | Model-predicted binary label: 0 or 1 |

### Optional reported-metrics JSON

```json
{
  "positive_label": 1,
  "tolerance": 0.005,
  "metrics": {
    "accuracy": 0.90,
    "precision": 0.90,
    "recall": 0.90,
    "f1": 0.90,
    "specificity": 0.90
  }
}
```

All reported metric values must be between 0 and 1. The tolerance is an absolute difference, not a relative percentage.

## Checks performed

- Recalculates accuracy, precision, recall, F1 and specificity from valid binary-label rows.
- Estimates percentile-bootstrap confidence intervals for those metrics (1,000 resamples, fixed seed) when at least two valid rows are available.
- Records the source CSV SHA-256, optional claims-file SHA-256, run timestamp, configuration and bootstrap settings in a reproducibility manifest.
- Compares supplied claims with recalculated metrics.
- Flags missing required values and invalid binary labels.
- Flags duplicate record IDs.
- Flags exact record IDs appearing in multiple dataset splits.
- Reports sample counts and split counts.
- Exports a JSON evidence record and a self-contained HTML report.

## Interpretation

- **PASS** — the specific configured check found no issue in the supplied evidence.
- **FLAG** — a discrepancy or structural issue needs review.
- **NOT_TESTED** — the evidence required for that check was not supplied or the check did not apply.

A flag is not proof of misconduct. A pass is not a certification.

## Explicit limitations

This application does not establish:
- that ground-truth labels are correct;
- that the export is complete or representative;
- semantic duplicates, near-duplicates, or indirect data leakage;
- statistical validity beyond the implemented row-level bootstrap intervals; the bootstrap assumes independent and identically distributed rows and estimates sampling variability only;
- fairness, robustness, security, safety, or production performance;
- whether the model creates commercial value.

Bootstrap intervals are not a substitute for a study-design review. They do not correct sampling bias, dependence between observations, benchmark contamination or invalid labels. The tool is a technical review aid, not an audit opinion, legal opinion, certification, or investment recommendation.

## Data handling

The application is designed to run locally. If deployed to a hosted environment, the operator must review hosting, access controls, retention, logging, backups, and confidentiality terms before accepting sensitive diligence data. Do not upload confidential transaction material to an unreviewed deployment.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Product scope

The current supported workflow is binary classification, including row-level percentile-bootstrap intervals for selected metrics. Regression, ranking, generative-AI evaluations, statistical uncertainty, benchmark provenance and richer experiment metadata are not represented as supported capabilities.
