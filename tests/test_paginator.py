from unittest.mock import AsyncMock

import pytest

from app.core.paginator import EventsPaginator


@pytest.mark.asyncio
async def test_paginator_iterates_all_pages():
    client_mock = AsyncMock()

    # Имитация получения первой страницы
    async def mock_get_events(changed_at, cursor=None):
        return {
            "next": "http://test?cursor=abc",
            "results": [{"id": 1}],
        }

    # Имитация получения следующей страницы
    async def mock_get_events_by_url(url):
        return {
            "next": None,
            "results": [{"id": 2}],
        }

    client_mock.get_events = mock_get_events
    client_mock.get_events_by_url = mock_get_events_by_url

    paginator = EventsPaginator(client_mock, "2000-01-01")

    results = []
    async for event in paginator:
        results.append(event)

    assert results == [{"id": 1}, {"id": 2}]