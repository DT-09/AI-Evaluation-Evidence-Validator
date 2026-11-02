"""Buyer-owned AI acceptance protocol evaluation and change evidence."""
from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter
from typing import Any

ENGINE_VERSION = "0.1.0"
ALLOWED_TYPES = {"exact_match", "allowed_values", "required_field", "regex_match", "human_review"}
ALLOWED_SEVERITIES = {"critical", "major", "minor"}
ALLOWED_REVIEW_DECISIONS = {"PASS", "FAIL", "INCONCLUSIVE"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_json_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} must be valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain a JSON object.")
    return value


def validate_protocol(protocol: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("protocol_id", "version", "workflow", "criteria", "decision_rules"):
        if key not in protocol:
            errors.append(f"Missing protocol field: {key}")
    for key in ("protocol_id", "version", "workflow"):
        value = protocol.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} must be a non-empty string.")
    if not isinstance(protocol.get("criteria"), list) or not protocol.get("criteria"):
        errors.append("criteria must be a non-empty array.")
        return errors
    ids: set[str] = set()
    for index, criterion in enumerate(protocol["criteria"]):
        prefix = f"criteria[{index}]"
        if not isinstance(criterion, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        cid = criterion.get("criterion_id")
        if not isinstance(cid, str) or not cid.strip():
            errors.append(f"{prefix}.criterion_id must be a non-empty string.")
        elif cid in ids:
            errors.append(f"Duplicate criterion_id: {cid}")
        else:
            ids.add(cid)
        if criterion.get("type") not in ALLOWED_TYPES:
            errors.append(f"{prefix}.type must be one of {sorted(ALLOWED_TYPES)}.")
        if criterion.get("severity") not in ALLOWED_SEVERITIES:
            errors.append(f"{prefix}.severity must be one of {sorted(ALLOWED_SEVERITIES)}.")
        threshold = criterion.get("minimum_pass_rate", 1.0)
        if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
            errors.append(f"{prefix}.minimum_pass_rate must be between 0 and 1.")
        if criterion.get("type") in {"exact_match", "required_field", "regex_match"} and not criterion.get("field"):
            errors.append(f"{prefix}.field is required for this criterion type.")
        if criterion.get("type") == "allowed_values":
            values = criterion.get("allowed_values")
            if not isinstance(criterion.get("field"), str) or not criterion.get("field").strip() or not isinstance(values, list) or not values:
                errors.append(f"{prefix} requires a non-empty field and allowed_values array.")
        if criterion.get("type") == "regex_match":
            pattern = criterion.get("pattern")
            if not isinstance(pattern, str) or not pattern:
                errors.append(f"{prefix}.pattern must be a non-empty regular expression.")
            else:
                try:
                    re.compile(pattern)
                except re.error as exc:
                    errors.append(f"{prefix}.pattern is invalid: {exc}")
    rules = protocol.get("decision_rules", {})
    if not isinstance(rules, dict):
        errors.append("decision_rules must be an object.")
    else:
        for key in ("minimum_overall_pass_rate", "minimum_case_coverage"):
            value = rules.get(key, 1.0)
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                errors.append(f"decision_rules.{key} must be between 0 and 1.")
        hard = rules.get("hard_fail_severities", ["critical"])
        if not isinstance(hard, list) or any(x not in ALLOWED_SEVERITIES for x in hard):
            errors.append("decision_rules.hard_fail_severities contains an invalid severity.")
    return errors


def _decode_object(value: Any, label: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a JSON object or JSON string.")
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} contains invalid JSON: {exc}") from exc
    if not isinstance(decoded, dict):
        raise ValueError(f"{label} must decode to a JSON object.")
    return decoded


def evaluate_run(
    protocol: dict[str, Any],
    cases: list[dict[str, Any]],
    run: list[dict[str, Any]],
    reviews: list[dict[str, Any]] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors = validate_protocol(protocol)
    if errors:
        raise ValueError("Invalid acceptance protocol: " + "; ".join(errors))
    if not cases:
        raise ValueError("The case set is empty.")
    if not run:
        raise ValueError("The system run is empty.")

    case_map: dict[str, dict[str, Any]] = {}
    for row in cases:
        case_id = str(row.get("case_id", "")).strip()
        if not case_id:
            raise ValueError("Every test case needs a non-empty case_id.")
        if case_id in case_map:
            raise ValueError(f"Duplicate test case ID: {case_id}")
        case_map[case_id] = row

    run_map: dict[str, dict[str, Any]] = {}
    for row in run:
        case_id = str(row.get("case_id", "")).strip()
        if not case_id:
            raise ValueError("Every run row needs a non-empty case_id.")
        if case_id in run_map:
            raise ValueError(f"Duplicate run case ID: {case_id}")
        run_map[case_id] = row

    review_map: dict[tuple[str, str], dict[str, Any]] = {}
    criterion_types = {c["criterion_id"]: c["type"] for c in protocol["criteria"]}
    for review in reviews or []:
        key = (str(review.get("case_id", "")).strip(), str(review.get("criterion_id", "")).strip())
        decision = str(review.get("decision", "")).strip().upper()
        if not all(key):
            raise ValueError("Every review needs case_id and criterion_id.")
        if key[0] not in case_map:
            raise ValueError(f"Review references unknown case_id: {key[0]}")
        if key[1] not in criterion_types or criterion_types[key[1]] != "human_review":
            raise ValueError(f"Review references a criterion that is not configured for human review: {key[1]}")
        if decision not in ALLOWED_REVIEW_DECISIONS:
            raise ValueError(f"Invalid review decision for {key}: {decision}")
        if key in review_map:
            raise ValueError(f"Duplicate review decision for {key}.")
        review_map[key] = {**review, "decision": decision}

    result_rows: list[dict[str, Any]] = []
    criterion_results: dict[str, list[str]] = {}
    for case_id, case in case_map.items():
        run_row = run_map.get(case_id)
        if run_row is None:
            for criterion in protocol["criteria"]:
                cid = criterion["criterion_id"]
                if cid in _case_criteria(case, protocol):
                    result_rows.append({
                        "case_id": case_id, "criterion_id": cid,
                        "severity": criterion["severity"], "status": "MISSING",
                        "detail": "No output was supplied for this test case."
                    })
                    criterion_results.setdefault(cid, []).append("MISSING")
            continue
        output = _decode_object(run_row.get("output_json", {}), f"output_json for {case_id}")
        expected = _decode_object(case.get("expected_json", {}), f"expected_json for {case_id}")
        applicable = _case_criteria(case, protocol)
        for criterion in protocol["criteria"]:
            cid = criterion["criterion_id"]
            if cid not in applicable:
                continue
            ctype = criterion["type"]
            field = criterion.get("field")
            status = "INCONCLUSIVE"
            detail = ""
            if ctype == "human_review":
                review = review_map.get((case_id, cid))
                if review:
                    status = review["decision"]
                    detail = str(review.get("rationale", "")) or "Human review decision recorded."
                else:
                    detail = "Human review decision is missing."
            elif ctype == "exact_match":
                if field not in output or criterion.get("expected_field", field) not in expected:
                    detail = "Output field or expected field is missing."
                elif output[field] == expected[criterion.get("expected_field", field)]:
                    status, detail = "PASS", "Output field matches the buyer-defined expected value."
                else:
                    status, detail = "FAIL", f"Expected {expected[criterion.get('expected_field', field)]!r}; received {output[field]!r}."
            elif ctype == "allowed_values":
                if field not in output:
                    detail = "Required output field is missing."
                elif output[field] in criterion["allowed_values"]:
                    status, detail = "PASS", "Output value is in the buyer-defined allowed set."
                else:
                    status, detail = "FAIL", f"Value {output[field]!r} is outside the allowed set."
            elif ctype == "required_field":
                value = output.get(field)
                if value is not None and value != "":
                    status, detail = "PASS", "Required output field is present."
                else:
                    status, detail = "FAIL", "Required output field is missing or empty."
            elif ctype == "regex_match":
                import re
                value = output.get(field)
                pattern = criterion.get("pattern", "")
                if value is None:
                    detail = "Output field is missing."
                elif re.search(pattern, str(value)):
                    status, detail = "PASS", "Output field matches the buyer-defined pattern."
                else:
                    status, detail = "FAIL", "Output field does not match the buyer-defined pattern."
            result_rows.append({
                "case_id": case_id, "criterion_id": cid, "severity": criterion["severity"],
                "status": status, "detail": detail
            })
            criterion_results.setdefault(cid, []).append(status)

    extra_case_ids = sorted(set(run_map) - set(case_map))
    expected_pairs = sum(len(_case_criteria(case, protocol)) for case in case_map.values())
    assessed_pairs = len(result_rows)
    applicable_case_ids = {r["case_id"] for r in result_rows}
    case_coverage = len(set(case_map) & set(run_map)) / len(case_map) if case_map else 0.0

    summaries = []
    all_statuses = [row["status"] for row in result_rows]
    for criterion in protocol["criteria"]:
        cid = criterion["criterion_id"]
        statuses = criterion_results.get(cid, [])
        decisive = [s for s in statuses if s in {"PASS", "FAIL"}]
        pass_rate = decisive.count("PASS") / len(decisive) if decisive else None
        summaries.append({
            "criterion_id": cid, "severity": criterion["severity"],
            "applicable_count": len(statuses), "pass_count": statuses.count("PASS"),
            "fail_count": statuses.count("FAIL"), "inconclusive_count": statuses.count("INCONCLUSIVE"),
            "missing_count": statuses.count("MISSING"), "pass_rate": pass_rate,
            "minimum_pass_rate": criterion.get("minimum_pass_rate", 1.0)
        })

    decisive_all = [s for s in all_statuses if s in {"PASS", "FAIL"}]
    overall_rate = decisive_all.count("PASS") / len(decisive_all) if decisive_all else None
    criteria_without_cases = [s["criterion_id"] for s in summaries if s["applicable_count"] == 0]
    missing_or_inconclusive = any(s in {"MISSING", "INCONCLUSIVE"} for s in all_statuses) or bool(criteria_without_cases) or bool(extra_case_ids)
    hard_severities = protocol.get("decision_rules", {}).get("hard_fail_severities", ["critical"])
    hard_failures = [r for r in result_rows if r["status"] == "FAIL" and r["severity"] in hard_severities]
    threshold_failures = [
        s for s in summaries
        if s["pass_rate"] is not None and s["pass_rate"] < s["minimum_pass_rate"]
    ]
    rules = protocol.get("decision_rules", {})
    minimum_coverage = rules.get("minimum_case_coverage", 1.0)
    minimum_overall = rules.get("minimum_overall_pass_rate", 1.0)

    if hard_failures or threshold_failures or (overall_rate is not None and overall_rate < minimum_overall):
        decision = "FAIL"
    elif case_coverage < minimum_coverage or missing_or_inconclusive or overall_rate is None:
        decision = "INSUFFICIENT EVIDENCE"
    else:
        decision = "PASS"

    return {
        "product": "Buyer-side AI Acceptance Assurance",
        "engine_version": ENGINE_VERSION,
        "protocol": {
            "protocol_id": protocol["protocol_id"], "version": protocol["version"],
            "workflow": protocol["workflow"], "case_set_version": protocol.get("case_set_version", "unspecified")
        },
        "metadata": metadata or {},
        "decision": decision,
        "summary": {
            "case_count": len(case_map), "run_case_count": len(run_map),
            "case_coverage": case_coverage, "expected_case_criterion_pairs": expected_pairs,
            "assessed_pairs": assessed_pairs, "overall_pass_rate": overall_rate,
            "hard_failure_count": len(hard_failures), "threshold_failure_count": len(threshold_failures),
            "extra_run_case_ids": extra_case_ids
        },
        "criterion_summary": summaries,
        "case_results": result_rows,
        "decision_rules": rules,
        "limitations": [
            "A PASS means only that the supplied run met the stated protocol and evidence coverage rules.",
            "The engine does not establish that buyer-defined test cases are representative or complete.",
            "Deterministic checks establish only the explicit condition they test; they do not infer semantic correctness.",
            "Human review quality depends on reviewer expertise, rubric clarity and adjudication.",
            "This is an acceptance-workflow aid, not a safety certification, legal opinion or regulatory compliance determination."
        ]
    }


def _case_criteria(case: dict[str, Any], protocol: dict[str, Any]) -> set[str]:
    raw = case.get("criterion_ids", "")
    if isinstance(raw, list):
        selected = {str(x).strip() for x in raw}
    else:
        selected = {x.strip() for x in str(raw).split(";") if x.strip()}
    known = {c["criterion_id"] for c in protocol["criteria"]}
    unknown = selected - known
    if unknown:
        raise ValueError(f"Test case {case.get('case_id')} references unknown criteria: {sorted(unknown)}")
    if not selected:
        raise ValueError(f"Test case {case.get('case_id')} must reference at least one criterion.")
    return selected


def compare_runs(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    def index(report: dict[str, Any]) -> dict[tuple[str, str], str]:
        return {(r["case_id"], r["criterion_id"]): r["status"] for r in report["case_results"]}
    old, new = index(baseline), index(candidate)
    changes = []
    for key in sorted(set(old) | set(new)):
        before, after = old.get(key, "NOT_PRESENT"), new.get(key, "NOT_PRESENT")
        if before != after:
            if before == "PASS" and after in {"FAIL", "MISSING", "INCONCLUSIVE"}:
                change = "REGRESSION"
            elif before in {"FAIL", "MISSING", "INCONCLUSIVE"} and after == "PASS":
                change = "RESOLVED"
            else:
                change = "CHANGED"
            changes.append({
                "case_id": key[0], "criterion_id": key[1],
                "baseline": before, "candidate": after, "change": change
            })
    return {
        "baseline_decision": baseline["decision"],
        "candidate_decision": candidate["decision"],
        "regression_count": sum(x["change"] == "REGRESSION" for x in changes),
        "resolved_count": sum(x["change"] == "RESOLVED" for x in changes),
        "changes": changes
    }


def render_html_report(report: dict[str, Any], comparison: dict[str, Any] | None = None) -> str:
    rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(str(r["case_id"])), html.escape(str(r["criterion_id"])),
            html.escape(str(r["severity"])), html.escape(str(r["status"])),
            html.escape(str(r["detail"]))
        ) for r in report["case_results"]
    )
    criteria = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}/{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(s["criterion_id"]), html.escape(s["severity"]),
            s["pass_count"], s["applicable_count"],
            "N/A" if s["pass_rate"] is None else f'{s["pass_rate"]:.1%}',
            f'{s["minimum_pass_rate"]:.1%}'
        ) for s in report["criterion_summary"]
    )
    comparison_html = ""
    if comparison is not None:
        comp_rows = "".join(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(x["case_id"]), html.escape(x["criterion_id"]),
                html.escape(x["baseline"]), html.escape(x["candidate"]), html.escape(x["change"])
            ) for x in comparison["changes"]
        )
        comparison_html = f"<h2>Change comparison</h2><p>Regressions: {comparison['regression_count']} · Resolved: {comparison['resolved_count']}</p><table><tr><th>Case</th><th>Criterion</th><th>Baseline</th><th>Candidate</th><th>Change</th></tr>{comp_rows}</table>"
    limitations = "".join(f"<li>{html.escape(x)}</li>" for x in report["limitations"])
    summary = report["summary"]
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Acceptance evidence report</title>
<style>body{{font:15px Arial,sans-serif;max-width:1100px;margin:40px auto;padding:0 20px;color:#202820}}h1,h2{{font-family:Georgia,serif}}.decision{{font-size:24px;font-weight:bold;padding:16px;border:1px solid #aaa}}table{{border-collapse:collapse;width:100%;margin:18px 0}}th,td{{border:1px solid #ddd;padding:9px;text-align:left;vertical-align:top}}th{{background:#f2f1eb}}small{{color:#666}}</style></head><body>
<p><small>BUYER-OWNED ACCEPTANCE EVIDENCE · {html.escape(report['engine_version'])}</small></p>
<h1>{html.escape(report['protocol']['workflow'])}</h1>
<p>Protocol {html.escape(report['protocol']['protocol_id'])} · version {html.escape(report['protocol']['version'])} · case set {html.escape(report['protocol']['case_set_version'])}</p>
<div class="decision">Decision: {html.escape(report['decision'])}</div>
<p>Case coverage: {summary['case_coverage']:.1%} · Overall pass rate: {'N/A' if summary['overall_pass_rate'] is None else f"{summary['overall_pass_rate']:.1%}"} · Hard failures: {summary['hard_failure_count']}</p>
<h2>Criterion summary</h2><table><tr><th>Criterion</th><th>Severity</th><th>Passes / applicable</th><th>Pass rate</th><th>Required</th></tr>{criteria}</table>
<h2>Case-level evidence</h2><table><tr><th>Case</th><th>Criterion</th><th>Severity</th><th>Status</th><th>Detail</th></tr>{rows}</table>
{comparison_html}<h2>Limitations</h2><ul>{limitations}</ul>
</body></html>"""
