from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",   
        extra="ignore",   
    )
    faq_api_url: str
    server_api_url: str
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "extra": "forbid"
    }

settings = Settings()