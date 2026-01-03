from typing import Any, Dict, List, Tuple

def recommend(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    apps = snapshot.get("scope", {}).get("applications", [])
    recs: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = snapshot.get("evidence", [])

    # Regla 1: lifecycle EOL/Retired
    for app in apps:
        lifecycle = str(app.get("lifecycle", "")).lower()
        if lifecycle in ("end of life", "eol", "retired", "decommissioned"):
            recs.append({
                "title": f"Plan de modernización para {app.get('name')}",
                "why": f"Lifecycle={app.get('lifecycle')} y criticality={app.get('criticality')}",
                "actions": [
                    "Definir target architecture y patrón de reemplazo (strangler / rewrite / COTS).",
                    "Evaluar impacto en integraciones (contratos API, eventos, dependencias).",
                    "Plan de migración con cutover controlado + pruebas E2E.",
                ],
                "factsheetId": app.get("id"),
            })

    # Regla 2: gaps de calidad
    # Si hay missingFields, recomendación de completar data
    quality = snapshot.get("quality") or {}
    missing = quality.get("missingFields") or []
    if missing:
        recs.append({
            "title": "Mejorar calidad de datos en LeanIX para aumentar exactitud",
            "why": f"Se detectaron {len(missing)} factsheets con campos obligatorios faltantes.",
            "actions": [
                "Completar owners (business/tech), lifecycle, criticality y lastUpdated.",
                "Alinear naming/aliases para resolver entidades sin ambigüedad.",
                "Modelar interfaces/capabilities mínimas para análisis de impacto.",
            ],
            "factsheetId": None,
        })

    return {"recommendations": recs, "evidence": evidence}
