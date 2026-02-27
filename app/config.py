from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "5432"
    DATABASE_NAME: str = "library_db"
    DATABASE_USER: str = "neo"
    DATABASE_PASSWORD: str = "Mo@3456@"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_EXPIRE: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
