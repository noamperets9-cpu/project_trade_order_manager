import asyncio

async def fetch_order_status(order_id: str) -> dict:
    """משימה עצמאית המדמה קבלת סטטוס של הזמנה (סימולציה של רשת)"""
    await asyncio.sleep(0.5) 
    return {"order_id": order_id, "status": "processed"}

async def collect_statuses_serially(order_ids: list) -> list:
    """גרסה סדרתית: ממתינה לסיום כל משימה לפני תחילת המשימה הבאה"""
    results = []
    for oid in order_ids:
        res = await fetch_order_status(oid)
        results.append(res)
    return results

async def collect_statuses_concurrently(order_ids: list) -> list:
    """גרסה אסינכרונית: תזמון של כל המשימות יחד בחפיפה לפני איסוף התוצאות"""
    tasks = [fetch_order_status(oid) for oid in order_ids]
    results = await asyncio.gather(*tasks)
    return results