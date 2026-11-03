"""Deterministic, analyst-confirmed financial observation comparison."""
from collections import defaultdict
from decimal import Decimal, InvalidOperation


def _num(value):
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    raw = raw.replace(",", "").replace("$", "").replace("€", "").replace("£", "").strip()
    if raw.startswith("(") and raw.endswith(")"):
        raw = "-" + raw[1:-1]
    try:
        number = Decimal(raw)
    except (InvalidOperation, ValueError):
        return None
    return number if number.is_finite() else None


def reconcile(observations, tolerance=Decimal("0.01")):
    """Compare confirmed observations without implicit unit or currency conversion.

    A finding is a review signal, not an accounting conclusion. Rows without a
    document, metric or period are excluded because they cannot be grouped safely.
    """
    tolerance = Decimal(str(tolerance))
    if not tolerance.is_finite() or tolerance < 0:
        raise ValueError("tolerance must be a finite, non-negative number")

    groups = defaultdict(list)
    for index, source in enumerate(observations):
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
            "_input_order": index,
        })
        groups[(metric.casefold(), period.casefold())].append(row)

    findings = []
    for key in sorted(groups):
        rows = groups[key]
        documents = {r["document"].casefold() for r in rows}
        units = {r["unit"].casefold() for r in rows}
        values = [_num(r.get("value")) for r in rows]
        numeric_values = [v for v in values if v is not None]

        if len(documents) < 2:
            status = "INSUFFICIENT_COVERAGE"
            explanation = "Fewer than two distinct source documents are represented."
        elif any(not r["unit"] or not r["source_ref"] for r in rows) or len(units) > 1:
            status = "MISSING_OR_NON_NUMERIC" if any(not r["unit"] or not r["source_ref"] for r in rows) else "UNIT_MISMATCH"
            explanation = (
                "At least one observation is missing its unit or source reference."
                if status == "MISSING_OR_NON_NUMERIC"
                else "Sources use different units; no conversion was attempted."
            )
        elif len(numeric_values) != len(rows):
            status = "MISSING_OR_NON_NUMERIC"
            explanation = "At least one value is blank or non-numeric."
        elif max(numeric_values) - min(numeric_values) > tolerance:
            status = "VALUE_MISMATCH"
            explanation = f"Observed spread: {max(numeric_values) - min(numeric_values)} {rows[0]['unit']}."
        else:
            status = "TIED"
            explanation = f"All supplied values agree within the configured tolerance ({tolerance})."

        for row in rows:
            row.pop("_input_order", None)
        findings.append({
            "metric": rows[0]["metric"],
            "period": rows[0]["period"],
            "status": status,
            "explanation": explanation,
            "source_count": len(documents),
            "observation_count": len(rows),
            "observations": rows,
        })
    return findings
