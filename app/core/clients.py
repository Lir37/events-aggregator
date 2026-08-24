from typing import Any
from urllib.parse import urljoin

import httpx

from app.config import settings


class EventsProviderClient:
    def __init__(self, base_url: str = settings.EVENTS_PROVIDER_URL, api_key: str = settings.EVENTS_PROVIDER_API_KEY):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_events(self, changed_at: str, cursor: str | None = None) -> dict[str, Any]:
        """Получить список событий (одна страница)"""
        url = urljoin(self.base_url, "/api/events/")
        params = {"changed_at": changed_at}
        if cursor:
            params["cursor"] = cursor
        response = await self._client.get(url, params=params, headers={"x-api-key": self.api_key})
        response.raise_for_status()
        return response.json()

    async def get_events_by_url(self, url: str) -> dict[str, Any]:
        """Получить страницу по полному URL (для пагинации)"""
        response = await self._client.get(url, headers={"x-api-key": self.api_key})
        response.raise_for_status()
        return response.json()

    async def get_seats(self, event_id: str) -> dict[str, Any]:
        """Получить список свободных мест"""
        url = urljoin(self.base_url, f"/api/events/{event_id}/seats/")
        response = await self._client.get(url, headers={"x-api-key": self.api_key})
        response.raise_for_status()
        return response.json()

    async def register(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> dict[str, Any]:
        """Зарегистрировать участника"""
        url = urljoin(self.base_url, f"/api/events/{event_id}/register/")
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat
        }
        response = await self._client.post(url, json=payload, headers={"x-api-key": self.api_key})
        response.raise_for_status()
        return response.json()

    async def unregister(self, event_id: str, ticket_id: str) -> dict[str, Any]:
        """Отменить регистрацию"""
        url = urljoin(self.base_url, f"/api/events/{event_id}/unregister/")
        payload = {"ticket_id": ticket_id}
        response = await self._client.request("DELETE", url, json=payload, headers={"x-api-key": self.api_key})
        response.raise_for_status()
        return response.json()