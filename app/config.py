from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "5432"
    DATABASE_NAME: str = "library_db"
    DATABASE_USER: str = "neo"
    DATABASE_PASSWORD: str = "Mo@3456@"

    class Config:
        env_file = ".env"

settings = Settings()
