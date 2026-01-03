from typing import Any, Dict, Optional
import httpx
from .config import settings

def _headers() -> Dict[str, str]:
    # Ajusta si tu LeanIX requiere otro header/flow
    return {
        "Authorization": f"Bearer {settings.leanix_api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

async def leanix_get(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    url = settings.leanix_api_base.rstrip("/") + "/" + path.lstrip("/")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()

async def leanix_post(path: str, payload: Dict[str, Any]) -> Any:
    url = settings.leanix_api_base.rstrip("/") + "/" + path.lstrip("/")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=_headers(), json=payload)
        r.raise_for_status()
        return r.json()
