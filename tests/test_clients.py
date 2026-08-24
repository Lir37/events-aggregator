import pytest
from unittest.mock import AsyncMock, patch
from app.core.clients import EventsProviderClient


@pytest.mark.asyncio
async def test_get_events():
    client = EventsProviderClient("http://test", "fake-key")
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.json = AsyncMock(return_value={"results": []})
        mock_get.return_value = mock_response

        result = await client.get_events("2000-01-01")
        assert result == {"results": []}


@pytest.mark.asyncio
async def test_register():
    client = EventsProviderClient("http://test", "fake-key")
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.json = AsyncMock(return_value={"ticket_id": "123"})
        mock_post.return_value = mock_response

        result = await client.register("event1", "John", "Doe", "john@example.com", "A1")
        assert result == {"ticket_id": "123"}