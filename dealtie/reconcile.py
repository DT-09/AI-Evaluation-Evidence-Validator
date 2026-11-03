from collections import defaultdict
from decimal import Decimal, InvalidOperation

def _num(value):
    if value is None or str(value).strip() == "": return None
    s=str(value).strip().replace(",", "").replace("$", "").replace("€", "").replace("£", "")
    if s.startswith("(") and s.endswith(")"): s="-"+s[1:-1]
    try: return Decimal(s)
    except InvalidOperation: return None

def reconcile(observations, tolerance=Decimal("0.01")):
    """Compare analyst-confirmed observations; never silently convert units."""
    groups=defaultdict(list)
    for row in observations:
        metric=str(row.get("metric","")).strip()
        period=str(row.get("period","")).strip()
        doc=str(row.get("document","")).strip()
        if metric and period and doc:
            groups[(metric.casefold(),period.casefold())].append({**row,"metric":metric,"period":period,"document":doc,"unit":str(row.get("unit","")).strip()})
    out=[]
    for _,rows in sorted(groups.items()):
        units={r["unit"].casefold() for r in rows if r["unit"]}
        vals=[_num(r.get("value")) for r in rows]
        nums=[v for v in vals if v is not None]
        if len({r["document"].casefold() for r in rows})<2: status="INSUFFICIENT_COVERAGE"; why="Only one source document is represented."
        elif len(units)>1: status="UNIT_MISMATCH"; why="Sources use different units; no conversion was attempted."
        elif len(nums)!=len(rows): status="MISSING_OR_NON_NUMERIC"; why="At least one value is blank or non-numeric."
        elif max(nums)-min(nums)>tolerance: status="VALUE_MISMATCH"; why=f"Observed spread: {max(nums)-min(nums)} {rows[0]['unit']}."
        else: status="TIED"; why="All supplied values agree within the configured tolerance."
        out.append({"metric":rows[0]["metric"],"period":rows[0]["period"],"status":status,"explanation":why,"source_count":len({r["document"].casefold() for r in rows}),"observations":rows})
    return out
