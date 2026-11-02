"""Deterministic evidence checks for binary-classification evaluations."""
from __future__ import annotations
import html, json, math, random
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any
import pandas as pd

REQUIRED_COLUMNS=("record_id","split","actual","predicted")
METRICS=("accuracy","precision","recall","f1","specificity")

@dataclass
class Check:
    check_id:str
    status:str
    summary:str
    details:list[str]

def _check(cid,status,summary,*details):
    return Check(cid,status,summary,list(details))

def _label(value):
    if pd.isna(value): return None
    value=str(value).strip()
    return int(value) if value in ("0","1") else None

def calculate_metrics(pairs:list[tuple[int,int]],positive_label:int=1)->dict[str,Any]:
    if positive_label not in (0,1): raise ValueError("positive_label must be 0 or 1")
    if not pairs: return {"sample_count":0,"confusion_matrix":None,"metrics":{m:None for m in METRICS}}
    tp=fp=tn=fn=0
    for actual,predicted in pairs:
        ap,pp=actual==positive_label,predicted==positive_label
        if ap and pp: tp+=1
        elif not ap and pp: fp+=1
        elif not ap and not pp: tn+=1
        else: fn+=1
    total=tp+fp+tn+fn
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    specificity=tn/(tn+fp) if tn+fp else None
    f1=2*precision*recall/(precision+recall) if precision is not None and recall is not None and precision+recall else None
    return {"sample_count":total,"confusion_matrix":{"tp":tp,"fp":fp,"tn":tn,"fn":fn},
            "metrics":{"accuracy":(tp+tn)/total,"precision":precision,"recall":recall,"f1":f1,"specificity":specificity}}


def bootstrap_metric_intervals(
    pairs: list[tuple[int, int]],
    positive_label: int = 1,
    n_resamples: int = 1000,
    confidence: float = 0.95,
    seed: int = 42,
) -> dict[str, Any]:
    """Percentile bootstrap intervals for row-level binary-classification metrics.

    Assumes evaluation rows are independent and identically distributed.
    This estimates sampling variability only; it does not establish dataset
    representativeness or correct benchmark construction.
    """
    if positive_label not in (0, 1):
        raise ValueError("positive_label must be 0 or 1")
    if n_resamples < 100:
        raise ValueError("n_resamples must be at least 100")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if len(pairs) < 2:
        return {
            "method": "non-parametric percentile bootstrap",
            "confidence_level": confidence,
            "n_resamples": n_resamples,
            "seed": seed,
            "status": "NOT_ESTIMATED",
            "reason": "At least two valid evaluation rows are required.",
            "intervals": {name: None for name in METRICS},
        }

    rng = random.Random(seed)
    samples: dict[str, list[float]] = {name: [] for name in METRICS}
    n = len(pairs)
    for _ in range(n_resamples):
        draw = [pairs[rng.randrange(n)] for _ in range(n)]
        values = calculate_metrics(draw, positive_label)["metrics"]
        for name, value in values.items():
            if value is not None and math.isfinite(value):
                samples[name].append(value)

    alpha = (1.0 - confidence) / 2.0

    def percentile(values: list[float], probability: float) -> float | None:
        if not values:
            return None
        ordered = sorted(values)
        position = (len(ordered) - 1) * probability
        lower = math.floor(position)
        upper = math.ceil(position)
        if lower == upper:
            return ordered[lower]
        weight = position - lower
        return ordered[lower] * (1 - weight) + ordered[upper] * weight

    intervals = {}
    for name, values in samples.items():
        intervals[name] = {
            "lower": percentile(values, alpha),
            "upper": percentile(values, 1 - alpha),
            "valid_resamples": len(values),
        } if values else None

    return {
        "method": "non-parametric percentile bootstrap",
        "confidence_level": confidence,
        "n_resamples": n_resamples,
        "seed": seed,
        "status": "COMPUTED",
        "assumption": "Evaluation rows are independent and identically distributed.",
        "interpretation": "Intervals estimate sampling variability only; they do not establish representativeness, label correctness, or benchmark validity.",
        "intervals": intervals,
    }

def _compare(metrics,reported,tolerance):
    checks=[]
    for name in METRICS:
        if name not in reported.get("metrics",{}):
            checks.append(_check(f"claim.{name}","NOT_TESTED",f"No reported {name} was supplied.")); continue
        try: claimed=float(reported["metrics"][name])
        except (TypeError,ValueError):
            checks.append(_check(f"claim.{name}","FLAG",f"Reported {name} is not numeric.")); continue
        actual=metrics.get(name)
        if not math.isfinite(claimed) or not 0<=claimed<=1:
            checks.append(_check(f"claim.{name}","FLAG",f"Reported {name} must be between 0 and 1.")); continue
        if actual is None:
            checks.append(_check(f"claim.{name}","NOT_TESTED",f"{name} cannot be calculated.")); continue
        delta=abs(actual-claimed)
        status="PASS" if delta<=tolerance else "FLAG"
        summary="Reported value agrees within tolerance." if status=="PASS" else "Reported value differs from recalculation."
        checks.append(_check(f"claim.{name}",status,summary,f"Reported: {claimed:.6f}",
            f"Recalculated: {actual:.6f}",f"Absolute difference: {delta:.6f}; tolerance: {tolerance:.6f}"))
    return checks

def validate_dataframe(frame:pd.DataFrame,reported:dict[str,Any]|None=None,positive_label:int=1,tolerance:float=0.005)->dict[str,Any]:
    reported=reported or {}
    if positive_label not in (0,1): raise ValueError("positive_label must be 0 or 1")
    tolerance=float(tolerance)
    if not math.isfinite(tolerance) or not 0<=tolerance<=1: raise ValueError("tolerance must be between 0 and 1")
    checks=[]
    missing_columns=[c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing_columns:
        checks.append(_check("schema.required_columns","FLAG","Required columns are missing.",*missing_columns))
        metrics=calculate_metrics([],positive_label)
        return {"product":"AI Evaluation Evidence Validator","input":{"record_count":len(frame),"columns":list(frame.columns),"split_counts":{}},
                "configuration":{"positive_label":positive_label,"tolerance":tolerance},"recalculated":metrics,
                "checks":[asdict(c) for c in checks],"limitations":["Required columns were missing; no complete evaluation was possible."]}
    checks.append(_check("dataset.non_empty","PASS" if len(frame) else "FLAG",f"Loaded {len(frame)} rows." if len(frame) else "Dataset is empty."))
    work=frame.loc[:,REQUIRED_COLUMNS].copy()
    for col in REQUIRED_COLUMNS: work[col]=work[col].astype("string").str.strip()
    missing=[]
    for col in REQUIRED_COLUMNS:
        n=int(work[col].isna().sum()+(work[col]=="").fillna(False).sum())
        if n: missing.append(f"{col}: {n} blank value(s)")
    checks.append(_check("data.required_values","FLAG" if missing else "PASS","Blank required values detected." if missing else "No blank required values.",*missing))
    pairs=[]; invalid=[]
    for idx,row in work.iterrows():
        a,p=_label(row["actual"]),_label(row["predicted"])
        if a is None or p is None: invalid.append(f"CSV data row {idx+2}: actual={row['actual']!r}, predicted={row['predicted']!r}")
        else: pairs.append((a,p))
    checks.append(_check("data.binary_labels","FLAG" if invalid else "PASS",f"{len(invalid)} invalid binary-label row(s)." if invalid else "All labels are binary 0/1.",*invalid[:100]))
    checks.append(_check("metrics.input_coverage","FLAG" if len(pairs)!=len(work) else "PASS",f"Metrics use {len(pairs)} of {len(work)} rows.",
        "Resolve invalid labels before relying on metrics." if len(pairs)!=len(work) else "Every row is included."))
    ids=work["record_id"].fillna("").astype(str)
    nonblank=ids[ids!=""]; duplicated=sorted(nonblank[nonblank.duplicated(keep=False)].unique().tolist())
    checks.append(_check("data.duplicate_record_ids","FLAG" if duplicated else "PASS",f"{len(duplicated)} duplicate ID(s)." if duplicated else "No duplicate IDs detected.",*duplicated[:100]))
    id_splits=defaultdict(set)
    for rid,split in zip(ids.tolist(),work["split"].fillna("").astype(str).tolist()):
        if rid and split: id_splits[rid].add(split)
    overlaps=[f"{rid}: {', '.join(sorted(s))}" for rid,s in id_splits.items() if len(s)>1]
    checks.append(_check("data.cross_split_id_overlap","FLAG" if overlaps else "PASS",f"{len(overlaps)} ID(s) occur across splits." if overlaps else "No exact record-ID overlap across splits.",*overlaps[:100]))
    split_counts=Counter(work["split"].fillna("(blank)").replace("","(blank)").astype(str).tolist())
    metrics=calculate_metrics(pairs,positive_label)
    checks.extend(_compare(metrics["metrics"],reported,tolerance) if reported else [_check("claims.reported_metrics","NOT_TESTED","No reported metrics supplied.")])
    return {"product":"AI Evaluation Evidence Validator","input":{"record_count":len(frame),"columns":list(frame.columns),"split_counts":dict(split_counts)},
        "configuration":{"positive_label":positive_label,"tolerance":tolerance},"recalculated":metrics,"statistical_review":bootstrap_metric_intervals(pairs, positive_label), "checks":[asdict(c) for c in checks],
        "limitations":["Findings apply only to supplied exported records and stated configuration.",
        "Exact record-ID checks do not detect semantic duplicates, near-duplicates or indirect data leakage.",
        "A metric match does not establish representativeness, robustness, fairness, safety or production performance.",
        "Bootstrap intervals assume independent and identically distributed rows and estimate sampling variability only.",
        "The engine cannot verify label correctness or export completeness.",
        "This is a technical review aid, not an audit opinion, certification or investment recommendation."]}

def load_reported_metrics(file_bytes:bytes)->dict[str,Any]:
    payload=json.loads(file_bytes.decode("utf-8-sig"))
    if not isinstance(payload,dict) or not isinstance(payload.get("metrics",{}),dict):
        raise ValueError("JSON must be an object with an optional metrics object.")
    return payload

def render_html_report(result:dict[str,Any])->str:
    metrics=result["recalculated"]["metrics"]
    metric_rows="".join(f"<tr><td>{html.escape(n)}</td><td>{'Not calculable' if v is None else f'{v:.6f}'}</td></tr>" for n,v in metrics.items())
    check_rows=""
    for item in result["checks"]:
        details="<br>".join(html.escape(str(x)) for x in item["details"])
        check_rows+=f"<tr><td>{html.escape(item['check_id'])}</td><td><b>{html.escape(item['status'])}</b></td><td>{html.escape(item['summary'])}</td><td>{details}</td></tr>"
    limitations="".join(f"<li>{html.escape(x)}</li>" for x in result["limitations"])
    cm=result["recalculated"]["confusion_matrix"] or {}
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Evaluation Evidence Verification</title>
<style>body{{margin:0;background:#f4f2eb;color:#202820;font:15px/1.6 system-ui,sans-serif}}main{{max-width:1100px;margin:42px auto;padding:0 22px}}h1,h2{{font-family:Georgia,serif;font-weight:500}}h1{{font-size:36px}}section{{background:#fff;border:1px solid #deded3;padding:22px;margin:20px 0}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #deded3;vertical-align:top}}th{{background:#f0eee7}}.muted{{color:#657064}}.notice{{border-left:3px solid #9a7952}}</style></head><body><main>
<h1>AI Evaluation Evidence Verification</h1><p class="muted">Evidence-based recalculation · {result['input']['record_count']} supplied records</p>
<section><h2>Recalculated metrics</h2><table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>{metric_rows}</tbody></table>
<p><b>Confusion matrix:</b> TP {cm.get('tp','—')} · FP {cm.get('fp','—')} · TN {cm.get('tn','—')} · FN {cm.get('fn','—')}</p><p><b>Split counts:</b> {html.escape(json.dumps(result['input']['split_counts']))}</p></section>
<section><h2>Verification checks</h2><table><thead><tr><th>Check</th><th>Status</th><th>Finding</th><th>Details</th></tr></thead><tbody>{check_rows}</tbody></table></section>
<section class="notice"><h2>Scope and limitations</h2><ul>{limitations}</ul><small>A PASS is not a certification.</small></section></main></body></html>"""
