from unittest.mock import AsyncMock

import pytest

from app.core.paginator import EventsPaginator


@pytest.mark.asyncio
async def test_paginator_iterates_all_pages():
    client_mock = AsyncMock()
    client_mock.get_events.side_effect = [
        {"next": "http://test?cursor=abc", "results": [{"id": 1}]},
        {"next": None, "results": [{"id": 2}]},
    ]

    paginator = EventsPaginator(client_mock, "2000-01-01")
    results = []
    async for event in paginator:
        results.append(event)
    assert results == [{"id": 1}, {"id": 2}]