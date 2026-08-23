import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    # ---- БД ----
    # 1. Сначала пробуем готовую строку от провайдера
    _db_url = os.getenv("POSTGRES_CONNECTION_STRING")
    if _db_url:
        # Переводим в формат asyncpg
        DATABASE_URL = _db_url.replace("postgres://", "postgresql+asyncpg://")
    else:
        # 2. Если нет, пробуем DATABASE_URL
        _db_url = os.getenv("DATABASE_URL")
        if _db_url:
            DATABASE_URL = _db_url
        else:
            # 3. Собираем из отдельных переменных
            host = os.getenv("POSTGRES_HOST")
            port = os.getenv("POSTGRES_PORT", "5432")
            user = os.getenv("POSTGRES_USERNAME")
            password = os.getenv("POSTGRES_PASSWORD")
            db_name = os.getenv("POSTGRES_DATABASE_NAME")

            if not host or not user or not password or not db_name:
                DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/events_db"
            else:
                DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

    # ---- Events Provider ----
    EVENTS_PROVIDER_URL: str = os.getenv(
        "EVENTS_PROVIDER_URL",
        "http://events-provider.dev-2.python-labs.ru"
    )
    EVENTS_PROVIDER_API_KEY: str = os.getenv("EVENTS_PROVIDER_API_KEY", "")
    SYNC_INTERVAL_HOURS: int = int(os.getenv("SYNC_INTERVAL_HOURS", "24"))

    # Отладочный вывод
    print(f"DEBUG: DATABASE_URL = {DATABASE_URL}")

settings = Settings()