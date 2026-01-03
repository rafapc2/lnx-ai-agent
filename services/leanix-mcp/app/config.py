from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "local"
    leanix_api_base: str = "https://your-leanix.example/api"
    leanix_api_token: str = "replace_me"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
