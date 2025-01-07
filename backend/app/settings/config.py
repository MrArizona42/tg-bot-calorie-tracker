from pydantic_settings import BaseSettings
from pydantic import computed_field


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DATABASE_HOST: str = 'db'
    DATABASE_PORT: str = '5432'

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DATABASE_HOST}\
            :{self.DATABASE_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = "../../.env"


settings = Settings()
print('*'*50)
print(settings.DATABASE_URL)
