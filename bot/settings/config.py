from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    FASTAPI_URL: str

    class Config:
        env_file = "../.env"


settings = Settings()
