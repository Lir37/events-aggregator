from typing import Any

from app.core.clients import EventsProviderClient


class EventsPaginator:
    """Асинхронный итератор для обхода всех страниц событий"""

    def __init__(
        self,
        client: EventsProviderClient,
        changed_at: str,
    ):
        self.client = client
        self.changed_at = changed_at
        self._current_page: dict[str, Any] | None = None
        self._current_index = 0
        self._next_url: str | None = None

    def __aiter__(self) -> "EventsPaginator":
        return self

    async def __anext__(self) -> dict[str, Any]:
        while (
            self._current_page is None
            or self._current_index
            >= len(self._current_page.get("results", []))
        ):
            if (
                self._current_page is not None
                and self._next_url is None
            ):
                raise StopAsyncIteration

            if self._current_page is None:
                data = await self.client.get_events(
                    self.changed_at
                )
            else:
                data = await self.client.get_events_by_url(
                    self._next_url
                )

            self._current_page = data
            self._current_index = 0
            self._next_url = data.get("next")

            if (
                not self._current_page.get("results")
                and self._next_url is None
            ):
                raise StopAsyncIteration
            

        event = self._current_page["results"][
            self._current_index
        ]
        self._current_index += 1

        return event