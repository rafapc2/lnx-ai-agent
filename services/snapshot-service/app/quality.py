from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

REQUIRED_APP_FIELDS = ["id", "name", "lifecycle", "criticality", "owners", "lastUpdated"]

def _parse_dt(s: str) -> datetime | None:
    try:
        # soporta ISO 8601 con Z
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s).astimezone(timezone.utc)
    except Exception:
        return None

def compute_quality(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    apps: List[Dict[str, Any]] = snapshot.get("scope", {}).get("applications", [])
    now = datetime.now(timezone.utc)

    missing_fields: List[Dict[str, Any]] = []
    freshness_days: List[int] = []
    completeness_scores: List[float] = []
    conflicts: List[str] = []

    for app in apps:
        missing = [f for f in REQUIRED_APP_FIELDS if f not in app or app.get(f) in (None, "", {}, [])]
        if missing:
            missing_fields.append({"factsheetId": app.get("id"), "missing": missing})
        completeness_scores.append(1.0 - (len(missing) / len(REQUIRED_APP_FIELDS)))

        dt = _parse_dt(str(app.get("lastUpdated", "")))
        if dt:
            freshness_days.append((now - dt).days)

        # ejemplo de conflicto simple
        if str(app.get("lifecycle", "")).lower() in ("retired", "decommissioned") and app.get("criticality") in ("High", "Critical"):
            conflicts.append(f"App {app.get('id')} retired pero criticality alta (revisar).")

    freshness_score = 1.0
    if freshness_days:
        # penaliza si es muy viejo
        avg_days = sum(freshness_days) / len(freshness_days)
        freshness_score = max(0.0, min(1.0, 1.0 - (avg_days / 180.0)))  # 180d = score 0
    completeness_score = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0

    coverage = {
        "apps_count": len(apps),
        "interfaces_modeled": snapshot.get("scope", {}).get("interfaces_count", 0),
        "capabilities_mapped": snapshot.get("scope", {}).get("capabilities_count", 0),
    }

    return {
        "freshnessScore": round(freshness_score, 3),
        "completenessScore": round(completeness_score, 3),
        "missingFields": missing_fields,
        "conflicts": conflicts,
        "coverage": coverage,
    }
