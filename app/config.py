import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    # ---- БД ----
    # Если задана строка подключения целиком – используем её
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+asyncpg://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DATABASE_NAME')}"
    )
    # ---- Events Provider ----
    EVENTS_PROVIDER_URL: str = os.getenv(
        "EVENTS_PROVIDER_URL",
        "http://events-provider.dev-2.python-labs.ru"
    )
    EVENTS_PROVIDER_API_KEY: str = os.getenv("EVENTS_PROVIDER_API_KEY", "")
    SYNC_INTERVAL_HOURS: int = int(os.getenv("SYNC_INTERVAL_HOURS", "24"))

settings = Settings()