import pytest
from project_name.async_processing import collect_statuses_serially, collect_statuses_concurrently

@pytest.mark.asyncio
async def test_async_vs_serial_results():
    """מוודא שהתוצאות בשתי הגרסאות זהות ומוחזרות לפי סדר הקלט"""
    order_ids = ["O1", "O2", "O3"]
    
    serial_results = await collect_statuses_serially(order_ids)
    concurrent_results = await collect_statuses_concurrently(order_ids)
    
    assert serial_results == concurrent_results
    assert len(concurrent_results) == 3
    assert [res["order_id"] for res in concurrent_results] == ["O1", "O2", "O3"]