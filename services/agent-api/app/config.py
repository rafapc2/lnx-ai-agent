from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "local"
    snapshot_service_url: str = "http://snapshot-service:8001"
    leanix_mcp_url: str = "http://leanix-mcp:8002"
    agent_require_evidence: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
