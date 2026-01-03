from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class SearchRequest(BaseModel):
    type: str = Field(..., description="FactSheet type (e.g., Application, Initiative)")
    query: Optional[str] = Field(None, description="Free text query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Field filters")

class ResolveInitiativeRequest(BaseModel):
    name_or_id: str
