from unittest.mock import AsyncMock

import pytest

from app.core.paginator import EventsPaginator


@pytest.mark.asyncio
async def test_paginator_iterates_all_pages():
    client_mock = AsyncMock()

    # Создаём асинхронную функцию для имитации get_events
    async def mock_get_events(changed_at, cursor=None):
        if cursor is None:
            return {"next": "http://test?cursor=abc", "results": [{"id": 1}]}
        else:
            return {"next": None, "results": [{"id": 2}]}

    client_mock.get_events = mock_get_events

    paginator = EventsPaginator(client_mock, "2000-01-01")
    results = []
    async for event in paginator:
        results.append(event)
    assert results == [{"id": 1}, {"id": 2}]