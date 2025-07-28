from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_BASE_URL: str
    FAQ_API_URL: str
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()