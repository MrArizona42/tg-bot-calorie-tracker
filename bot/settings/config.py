from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    FASTAPI_URL: str
    FOOD_API_KEY: str
    WEATHER_API_KEY: str

    class Config:
        env_file = "../.env"


settings = Settings()
