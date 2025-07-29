from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    faq_api_url: str
    debug: bool = False

    db_server: str
    db_name: str
    db_user: str
    db_password: str

    model_config = {
        "env_file": ".env",
        "extra": "forbid"
    }

settings = Settings()