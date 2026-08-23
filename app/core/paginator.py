from collections.abc import AsyncIterator
from typing import Any

from app.core.clients import EventsProviderClient


class EventsPaginator:
    """Асинхронный итератор для обхода всех страниц событий"""
    def __init__(self, client: EventsProviderClient, changed_at: str):
        self.client = client
        self.changed_at = changed_at
        self._current_page: dict[str, Any] | None = None
        self._current_index = 0
        self._next_url: str | None = None

    async def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        return self

    async def __anext__(self) -> dict[str, Any]:
        # Если нет текущей страницы или дошли до конца списка результатов
        if self._current_page is None or self._current_index >= len(self._current_page.get("results", [])):
            # Если есть следующая страница – загружаем, иначе конец
            if self._next_url is None and self._current_page is not None:
                raise StopAsyncIteration

            # Загружаем первую или следующую страницу
            if self._current_page is None:
                data = await self.client.get_events(self.changed_at)
            else:
                data = await self.client.get_events_by_url(self._next_url)

            self._current_page = data
            self._current_index = 0
            self._next_url = data.get("next")

        event = self._current_page["results"][self._current_index]
        self._current_index += 1
        return event