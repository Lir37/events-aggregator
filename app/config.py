import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    # ---- БД ----
    # Сначала пробуем взять готовую строку
    _db_url = os.getenv("DATABASE_URL")
    if _db_url:
        DATABASE_URL = _db_url
    else:
        # Собираем из отдельных переменных
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USERNAME")
        password = os.getenv("POSTGRES_PASSWORD")
        db_name = os.getenv("POSTGRES_DATABASE_NAME")

        # Проверяем, что все переменные заданы
        if not host or not user or not password or not db_name:
            # Если что-то не задано – подставляем значения для локальной разработки (можно изменить)
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

    # Для отладки – если ключ не задан, выводим предупреждение
    if not EVENTS_PROVIDER_API_KEY:
        print("WARNING: EVENTS_PROVIDER_API_KEY is not set!")

settings = Settings()