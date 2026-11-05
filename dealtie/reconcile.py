"""Deterministic, analyst-confirmed financial observation comparison."""
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import re


_NUMBER = re.compile(r"^[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d*)?|\.\d+)$")

# Operational review order only; this is not a financial materiality or risk score.
_REVIEW_PRIORITY = {
    "VALUE_MISMATCH": (1, "Resolve comparison"),
    "UNIT_MISMATCH": (1, "Resolve comparison"),
    "DUPLICATE_SOURCE_ENTRY": (2, "Resolve evidence quality"),
    "MISSING_OR_NON_NUMERIC": (2, "Resolve evidence quality"),
    "INSUFFICIENT_COVERAGE": (3, "Complete source coverage"),
    "TIED": (4, "No exception"),
}


def _num(value):
    """Parse a plain financial number without guessing currency or scale.

    Currency symbols are deliberately rejected: currency belongs in the
    explicit unit field. Commas are accepted only as valid thousands
    separators, so malformed values are never reinterpreted.
    """
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None

    negative_parentheses = raw.startswith("(") and raw.endswith(")")
    if negative_parentheses:
        raw = raw[1:-1].strip()
        if not raw or raw.startswith(("+", "-")):
            return None

    if raw.endswith(("%", "x", "X")):
        raw = raw[:-1].strip()

    if not _NUMBER.fullmatch(raw):
        return None

    normalized = raw.replace(",", "")
    if negative_parentheses:
        normalized = "-" + normalized

    try:
        number = Decimal(normalized)
    except (InvalidOperation, ValueError):
        return None
    return number if number.is_finite() else None


def reconcile(observations, tolerance=Decimal("0.01")):
    """Compare analyst-confirmed observations without implicit conversions.

    Rows that lack a document, metric or period cannot be grouped safely and
    are excluded. Duplicate document/source references are surfaced rather
    than silently counted as independent evidence.
    """
    try:
        tolerance = Decimal(str(tolerance))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("tolerance must be a finite, non-negative number") from exc
    if not tolerance.is_finite() or tolerance < 0:
        raise ValueError("tolerance must be a finite, non-negative number")

    groups = defaultdict(list)
    for source in observations:
        row = dict(source)
        metric = " ".join(str(row.get("metric", "")).split())
        period = " ".join(str(row.get("period", "")).split())
        document = " ".join(str(row.get("document", "")).split())
        if not (metric and period and document):
            continue
        row.update({
            "metric": metric,
            "period": period,
            "document": document,
            "unit": " ".join(str(row.get("unit", "")).split()),
            "source_ref": " ".join(str(row.get("source_ref", "")).split()),
        })
        groups[(metric.casefold(), period.casefold())].append(row)

    findings = []
    for key in sorted(groups):
        rows = groups[key]
        documents = {r["document"].casefold() for r in rows}
        units = {r["unit"].casefold() for r in rows if r["unit"]}
        source_keys = [
            (r["document"].casefold(), r["source_ref"].casefold())
            for r in rows if r["source_ref"]
        ]
        duplicate_sources = len(source_keys) != len(set(source_keys))
        values = [_num(r.get("value")) for r in rows]
        numeric_values = [v for v in values if v is not None]

        if duplicate_sources:
            status = "DUPLICATE_SOURCE_ENTRY"
            explanation = "The same document and source reference appears more than once for this metric and period. Review the repeated entry before relying on the comparison."
        elif len(documents) < 2:
            status = "INSUFFICIENT_COVERAGE"
            explanation = "Fewer than two distinct source documents are represented."
        elif any(not r["unit"] or not r["source_ref"] for r in rows):
            status = "MISSING_OR_NON_NUMERIC"
            explanation = "At least one observation is missing its unit or source reference."
        elif len(units) > 1:
            status = "UNIT_MISMATCH"
            explanation = "Sources use different units; no conversion was attempted."
        elif len(numeric_values) != len(rows):
            status = "MISSING_OR_NON_NUMERIC"
            explanation = "At least one value is blank, malformed or non-numeric."
        elif max(numeric_values) - min(numeric_values) > tolerance:
            status = "VALUE_MISMATCH"
            explanation = f"Observed spread: {max(numeric_values) - min(numeric_values)} {rows[0]['unit']}."
        else:
            status = "TIED"
            explanation = f"All supplied values agree within the configured tolerance ({tolerance})."

        priority, priority_label = _REVIEW_PRIORITY[status]
        findings.append({
            "metric": rows[0]["metric"],
            "period": rows[0]["period"],
            "status": status,
            "review_priority": priority,
            "review_priority_label": priority_label,
            "explanation": explanation,
            "source_count": len(documents),
            "observation_count": len(rows),
            "tolerance": str(tolerance),
            "observations": rows,
        })
    # Actionable comparison/evidence exceptions precede incomplete coverage
    # and tied metrics. Stable secondary keys keep repeated runs deterministic.
    findings.sort(key=lambda item: (
        item["review_priority"],
        item["metric"].casefold(),
        item["period"].casefold(),
    ))
    return findings
