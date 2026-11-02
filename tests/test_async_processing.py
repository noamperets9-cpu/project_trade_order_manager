import time

import pytest
from project_name.async_processing import collect_statuses_serially, collect_statuses_concurrently

# זמני תגובה הפוכים לסדר הקלט: O3 מסיימת ראשונה ו-O1 אחרונה
ORDER_IDS = ["O1", "O2", "O3"]
DELAYS = [0.15, 0.10, 0.05]


@pytest.mark.asyncio
async def test_async_vs_serial_results():
    """מוודא שהתוצאות בשתי הגרסאות זהות ומוחזרות לפי סדר הקלט"""
    serial_results = await collect_statuses_serially(ORDER_IDS, DELAYS)
    concurrent_results = await collect_statuses_concurrently(ORDER_IDS, DELAYS)

    assert serial_results == concurrent_results
    assert len(concurrent_results) == 3


@pytest.mark.asyncio
async def test_results_follow_input_order_even_when_finish_order_differs():
    results = await collect_statuses_concurrently(ORDER_IDS, DELAYS)

    assert [r["order_id"] for r in results] == ["O1", "O2", "O3"]


@pytest.mark.asyncio
async def test_known_order_gets_its_prepared_status():
    [result] = await collect_statuses_concurrently(["ORD1002"], [0.01])

    assert result == {"order_id": "ORD1002", "status": "בטיפול"}


@pytest.mark.asyncio
async def test_concurrent_version_runs_tasks_together():
    # סדרתי: סכום ההמתנות (0.30). אסינכרוני: בערך ההמתנה הארוכה (0.15)
    start = time.perf_counter()
    await collect_statuses_concurrently(ORDER_IDS, DELAYS)
    elapsed = time.perf_counter() - start

    assert elapsed < sum(DELAYS)
