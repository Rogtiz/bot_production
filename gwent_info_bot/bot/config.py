from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_SECRET_KEY: str

    API_URL: str

    class Config:
        env_file = ".env"


settings = Settings()