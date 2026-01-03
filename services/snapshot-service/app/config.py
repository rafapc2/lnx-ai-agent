from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "local"

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "leanix_agent"
    postgres_user: str = "leanix"
    postgres_password: str = "leanix_password"

    redis_host: str = "redis"
    redis_port: int = 6379

    leanix_mcp_url: str = "http://leanix-mcp:8002"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
