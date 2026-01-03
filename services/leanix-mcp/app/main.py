from fastapi import FastAPI, HTTPException
from typing import Any, Dict
from .models import SearchRequest, ResolveInitiativeRequest
from . import leanix_client

app = FastAPI(
    title="LeanIX MCP Connector (REST tools)",
    version="0.1.0",
    description="Wrapper REST para structured retrieval hacia LeanIX. Reemplaza/ajusta endpoints según tu MCP real.",
)

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

# ---------------------------
# Tools-like endpoints
# ---------------------------

@app.post("/fact_sheets/search")
async def fact_sheets_search(req: SearchRequest) -> Any:
    # MVP: si no configuras LeanIX real, devolvemos mock.
    if req.query is None and not req.filters:
        # mock simple
        return {"items": [], "note": "No query/filters provided. Configure LEANIX_* to use real API."}

    # Aquí deberías implementar el mapping real a LeanIX (GraphQL/REST) o a tu MCP.
    # Ejemplo genérico:
    try:
        # Placeholder: intenta llamar un endpoint real si existe en tu entorno
        # return await leanix_client.leanix_post("/factsheets/search", req.model_dump())
        return {
            "items": [],
            "note": "Implementa el mapping real a LeanIX aquí (search).",
            "request": req.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LeanIX search error: {e}")

@app.get("/fact_sheets/{factsheet_id}")
async def fact_sheet_get(factsheet_id: str) -> Any:
    # Mock data for local testing
    if factsheet_id.startswith("MOCK-"):
        return {
            "id": factsheet_id,
            "type": "Application",
            "name": "Mock App",
            "lifecycle": "End of Life",
            "criticality": "High",
            "owners": {"business": "Jane Doe", "tech": "John Doe"},
            "lastUpdated": "2026-01-01T00:00:00Z",
        }
    try:
        # return await leanix_client.leanix_get(f"/factsheets/{factsheet_id}")
        return {"note": "Implementa el mapping real a LeanIX aquí (get factsheet).", "id": factsheet_id}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LeanIX get error: {e}")

@app.get("/relations/{factsheet_id}")
async def relations_get(factsheet_id: str, depth: int = 1) -> Any:
    # Mock relations graph
    if factsheet_id.startswith("MOCK-"):
        return {
            "id": factsheet_id,
            "depth": depth,
            "relations": {
                "interfaces": [{"to": "MOCK-APP-2", "type": "REST"}],
                "capabilities": [{"id": "CAP-1", "name": "Payments"}],
                "tech": [{"id": "TRM-1", "name": "PostgreSQL"}],
            },
        }
    try:
        # return await leanix_client.leanix_get(f"/factsheets/{factsheet_id}/relations", params={"depth": depth})
        return {"note": "Implementa el mapping real a LeanIX aquí (relations).", "id": factsheet_id, "depth": depth}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LeanIX relations error: {e}")

@app.post("/initiatives/resolve")
async def resolve_initiative(req: ResolveInitiativeRequest) -> Any:
    # MVP: si viene un ID tipo INIT-*, lo devolvemos directo.
    val = req.name_or_id.strip()
    if val.upper().startswith("INIT-"):
        return {"initiative_id": val, "resolved_by": "rule:init-prefix"}

    # Si no, devolvemos un mock para pruebas locales
    return {"initiative_id": "INIT-123", "resolved_by": "mock", "input": val}
