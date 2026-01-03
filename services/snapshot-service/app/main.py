from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import httpx

from .config import settings
from .db import insert_snapshot, get_latest_snapshot
from .quality import compute_quality

app = FastAPI(
    title="Snapshot & Data Quality Service",
    version="0.1.0",
    description="Construye snapshots versionados (por iniciativa) y calcula calidad de datos.",
)

class BuildSnapshotRequest(BaseModel):
    initiative_id: str

class SnapshotResponse(BaseModel):
    id: int
    initiative_id: str
    snapshot: Dict[str, Any]
    quality: Dict[str, Any]

@app.get("/health")
def health():
    return {"status": "ok"}

async def _resolve_initiative(initiative_id: str) -> str:
    # Resuelve/normaliza (por ahora directo)
    return initiative_id

async def _build_mock_snapshot(initiative_id: str) -> Dict[str, Any]:
    # Snapshot canónico mínimo para pruebas locales
    return {
        "initiative": {
            "id": initiative_id,
            "name": f"Iniciativa {initiative_id}",
            "status": "In Progress",
            "regions": ["CL"],
        },
        "scope": {
            "applications": [
                {
                    "id": "MOCK-APP-1",
                    "name": "Core Banking Adapter",
                    "lifecycle": "End of Life",
                    "criticality": "High",
                    "owners": {"business": "Owner Biz", "tech": "Owner Tech"},
                    "lastUpdated": "2026-01-01T00:00:00Z",
                },
                {
                    "id": "MOCK-APP-2",
                    "name": "Payments Gateway",
                    "lifecycle": "Active",
                    "criticality": "High",
                    "owners": {"business": "Owner Biz 2", "tech": "Owner Tech 2"},
                    "lastUpdated": "2025-12-20T00:00:00Z",
                },
            ],
            "interfaces_count": 1,
            "capabilities_count": 1,
        },
        "tech": {"standards": [], "trm": []},
        "risk": {"findings": []},
        "evidence": [
            {"factsheetId": "MOCK-APP-1", "field": "lifecycle", "value": "End of Life", "lastUpdated": "2026-01-01T00:00:00Z"},
            {"factsheetId": "MOCK-APP-2", "field": "lifecycle", "value": "Active", "lastUpdated": "2025-12-20T00:00:00Z"},
        ],
    }

async def _build_snapshot_from_leanix(initiative_id: str) -> Dict[str, Any]:
    # En un entorno real:
    # 1) resolve iniciativa
    # 2) traer factsheets relacionados + relaciones
    # 3) materializar snapshot canónico (initiative/scope/tech/risk/evidence)
    # Por ahora: intenta resolver vía leanix-mcp; si no, usa mock.

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.post(f"{settings.leanix_mcp_url}/initiatives/resolve", json={"name_or_id": initiative_id})
            r.raise_for_status()
            resolved = r.json().get("initiative_id", initiative_id)
        except Exception:
            resolved = initiative_id

    # Si no hay integración real, devolvemos mock.
    return await _build_mock_snapshot(resolved)

@app.post("/snapshots/build", response_model=SnapshotResponse)
async def build_snapshot(req: BuildSnapshotRequest):
    init_id = (req.initiative_id or "").strip()
    if not init_id:
        raise HTTPException(status_code=400, detail="initiative_id is required")

    snapshot = await _build_snapshot_from_leanix(init_id)
    quality = compute_quality(snapshot)

    snapshot_id = insert_snapshot(init_id, snapshot, quality)
    return SnapshotResponse(id=snapshot_id, initiative_id=init_id, snapshot=snapshot, quality=quality)

@app.get("/snapshots/latest/{initiative_id}")
async def latest_snapshot(initiative_id: str):
    row = get_latest_snapshot(initiative_id)
    if not row:
        raise HTTPException(status_code=404, detail="No snapshot found")
    return row
