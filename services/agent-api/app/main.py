from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
import httpx

from .config import settings
from .recommender import recommend

app = FastAPI(
    title="LeanIX Agent API",
    version="0.1.0",
    description="Agente/orquestador simple: obtiene snapshot, calcula recomendaciones y responde con evidencia.",
)

class RecommendationRequest(BaseModel):
    initiative_id: str
    question: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok"}

async def _get_or_build_snapshot(initiative_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        # Intenta obtener el último snapshot
        r = await client.get(f"{settings.snapshot_service_url}/snapshots/latest/{initiative_id}")
        if r.status_code == 404:
            # build
            b = await client.post(f"{settings.snapshot_service_url}/snapshots/build", json={"initiative_id": initiative_id})
            b.raise_for_status()
            return b.json()["snapshot"] | {"quality": b.json()["quality"]}
        r.raise_for_status()
        row = r.json()
        return row["snapshot"] | {"quality": row["quality"]}

@app.post("/recommendations")
async def recommendations(req: RecommendationRequest):
    initiative_id = (req.initiative_id or "").strip()
    if not initiative_id:
        raise HTTPException(status_code=400, detail="initiative_id is required")

    snapshot = await _get_or_build_snapshot(initiative_id)
    result = recommend(snapshot)

    # Guardrail: si se requiere evidencia y no hay evidence, avisar
    if settings.agent_require_evidence and not result.get("evidence"):
        result["warnings"] = ["No evidence found in snapshot. Revisa integración LeanIX / snapshot builder."]

    result["initiative_id"] = initiative_id
    result["question"] = req.question
    result["data_quality"] = snapshot.get("quality", {})
    return result
