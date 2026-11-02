import asyncio

# ============================================================
#        שלב 2, סעיף 5.1 - איסוף סטטוסים סדרתי ואסינכרוני
# ============================================================
# כל משימה (קבלת סטטוס של פקודה אחת) עצמאית: היא לא צריכה תוצאה של משימה אחרת.
# זו סימולציה: ההמתנה מדומה עם asyncio.sleep, והנתונים מקומיים (ללא רשת).
# לכל פקודה זמן תגובה שונה, כך שסדר הסיום שונה מסדר הקלט,
# ובכל זאת התוצאות מוחזרות לפי סדר הקלט.

DEFAULT_DELAY = 0.5

# נתונים מקומיים שהוכנו מראש: הסטטוס שמערכת הביצוע "מחזירה" לכל פקודה
SIMULATED_STATUSES = {
    "ORD1001": "בוצעה",
    "ORD1002": "בטיפול",
    "ORD1003": "ממתינה",
}


async def fetch_order_status(order_id: str, delay: float = DEFAULT_DELAY) -> dict:
    """ משימה עצמאית המדמה קבלת סטטוס של פקודה (המתנה לא חוסמת) """
    await asyncio.sleep(delay)
    return {"order_id": order_id, "status": SIMULATED_STATUSES.get(order_id, "ממתינה")}


async def collect_statuses_serially(order_ids: list, delays: list = None) -> list:
    """ גרסה סדרתית: ממתינה לסיום כל משימה לפני תחילת המשימה הבאה """
    delays = delays or [DEFAULT_DELAY] * len(order_ids)
    results = []
    for oid, delay in zip(order_ids, delays):
        results.append(await fetch_order_status(oid, delay))
    return results


async def collect_statuses_concurrently(order_ids: list, delays: list = None) -> list:
    """ גרסה אסינכרונית: כל המשימות מתוזמנות יחד, ו-gather מחזיר את התוצאות לפי סדר הקלט """
    delays = delays or [DEFAULT_DELAY] * len(order_ids)
    tasks = [asyncio.create_task(fetch_order_status(oid, delay)) for oid, delay in zip(order_ids, delays)]
    return await asyncio.gather(*tasks)
