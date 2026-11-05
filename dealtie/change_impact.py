"""Deterministic version-change and downstream-reference analysis.

Only analyst-confirmed observations are compared. Matching is exact after
normalising whitespace/case for document family, metric, period and unit.
No semantic matching, unit conversion, source-authority inference or financial
judgement is performed.
"""
from collections import defaultdict
from decimal import Decimal, InvalidOperation


def _text(value):
    return " ".join(str(value or "").split())


def _decimal(value):
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError):
        return None
    return number if number.is_finite() else None


def _key(*values):
    return tuple(_text(value).casefold() for value in values)


def analyze_version_impact(observations, baseline_version, current_version, tolerance="0.01"):
    """Compare two versions of source families and map exact downstream references.

    Required row fields:
      document_family, version, document, metric, period, value, unit, source_ref

    A source-family change is detected only when the same family/metric/period
    exists in both selected versions. Other documents containing the exact
    metric/period are classified as candidates for human review:
      STALE_CANDIDATE: downstream value equals the old value, not the new one
      ALIGNED_TO_CURRENT: downstream value equals the new value
      OTHER_VALUE: downstream value equals neither
      INSUFFICIENT_EVIDENCE: missing/invalid value or unit conflict

    These are comparison states, not conclusions about which value is correct.
    """
    try:
        tol = Decimal(str(tolerance))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("tolerance must be a finite, non-negative number") from exc
    if not tol.is_finite() or tol < 0:
        raise ValueError("tolerance must be a finite, non-negative number")

    baseline = _text(baseline_version)
    current = _text(current_version)
    if not baseline or not current or baseline.casefold() == current.casefold():
        raise ValueError("baseline_version and current_version must be distinct, non-empty versions")

    rows = []
    for source in observations:
        row = dict(source)
        family = _text(row.get("document_family"))
        version = _text(row.get("version"))
        document = _text(row.get("document"))
        metric = _text(row.get("metric"))
        period = _text(row.get("period"))
        unit = _text(row.get("unit"))
        source_ref = _text(row.get("source_ref"))
        if family and version and document and metric and period:
            row.update({
                "document_family": family, "version": version,
                "document": document, "metric": metric, "period": period,
                "unit": unit, "source_ref": source_ref,
            })
            rows.append(row)

    version_groups = defaultdict(list)
    for row in rows:
        version_groups[_key(row["document_family"], row["version"], row["metric"], row["period"])].append(row)

    families = sorted({
        _key(row["document_family"])[0] for row in rows
        if row["version"].casefold() in {baseline.casefold(), current.casefold()}
    })
    changes = []
    for family_key in families:
        metric_periods = sorted({
            _key(row["metric"], row["period"])
            for row in rows
            if _key(row["document_family"])[0] == family_key
            and row["version"].casefold() in {baseline.casefold(), current.casefold()}
        })
        for metric_key in metric_periods:
            old_rows = version_groups.get((family_key, baseline.casefold(), *metric_key), [])
            new_rows = version_groups.get((family_key, current.casefold(), *metric_key), [])
            if not old_rows or not new_rows:
                continue
            old_units = {_key(row["unit"])[0] for row in old_rows if row["unit"]}
            new_units = {_key(row["unit"])[0] for row in new_rows if row["unit"]}
            old_values = [_decimal(row.get("value")) for row in old_rows]
            new_values = [_decimal(row.get("value")) for row in new_rows]
            if (len(old_units) != 1 or len(new_units) != 1 or old_units != new_units
                    or any(value is None for value in old_values + new_values)):
                continue
            old_min, old_max = min(old_values), max(old_values)
            new_min, new_max = min(new_values), max(new_values)
            if old_max - old_min > tol or new_max - new_min > tol:
                continue
            old_value, new_value = old_values[0], new_values[0]
            if abs(new_value - old_value) <= tol:
                continue

            metric = new_rows[0]["metric"]
            period = new_rows[0]["period"]
            unit = new_rows[0]["unit"]
            impact = []
            for row in rows:
                if _key(row["metric"], row["period"]) != metric_key:
                    continue
                if _key(row["document_family"])[0] == family_key:
                    continue
                value = _decimal(row.get("value"))
                row_unit = _key(row.get("unit"))[0]
                if value is None or row_unit != _key(unit)[0]:
                    state = "INSUFFICIENT_EVIDENCE"
                elif abs(value - old_value) <= tol and abs(value - new_value) > tol:
                    state = "STALE_CANDIDATE"
                elif abs(value - new_value) <= tol:
                    state = "ALIGNED_TO_CURRENT"
                else:
                    state = "OTHER_VALUE"
                impact.append({
                    "document_family": row["document_family"],
                    "version": row["version"],
                    "document": row["document"],
                    "value": str(row.get("value", "")),
                    "unit": row["unit"],
                    "source_ref": row["source_ref"],
                    "state": state,
                })
            changes.append({
                "source_family": new_rows[0]["document_family"],
                "metric": metric,
                "period": period,
                "unit": unit,
                "baseline_version": baseline,
                "current_version": current,
                "baseline_value": str(old_value),
                "current_value": str(new_value),
                "change": str(new_value - old_value),
                "baseline_sources": [
                    {"document": r["document"], "source_ref": r["source_ref"], "value": str(r.get("value", ""))}
                    for r in old_rows
                ],
                "current_sources": [
                    {"document": r["document"], "source_ref": r["source_ref"], "value": str(r.get("value", ""))}
                    for r in new_rows
                ],
                "downstream_references": impact,
                "stale_candidate_count": sum(item["state"] == "STALE_CANDIDATE" for item in impact),
                "review_required": True,
                "interpretation": "A version change was detected. Downstream references are candidates for human review; this analysis does not determine the authoritative figure.",
            })
    return sorted(changes, key=lambda item: (
        item["source_family"].casefold(), item["metric"].casefold(), item["period"].casefold()
    ))
