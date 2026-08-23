import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/events_db")
    EVENTS_PROVIDER_URL: str = os.getenv("EVENTS_PROVIDER_URL", "http://events-provider.dev-2.python-labs.ru")
    EVENTS_PROVIDER_API_KEY: str = os.getenv("EVENTS_PROVIDER_API_KEY", "")
    SYNC_INTERVAL_HOURS: int = int(os.getenv("SYNC_INTERVAL_HOURS", "24"))

settings = Settings()
