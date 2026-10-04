import os
from models import TradingPlatform
from repository import load_orders_from_file
from processing import (
    process_regular_queue,
    process_priority_queue,
    demonstrate_comprehensions,
    demonstrate_sorting
)
from iterators import OrderCollection, run_lazy_pipeline
from context_managers import OrderProcessingContext


# ============================================================
#                 חלק ה' - תרחיש ההדגמה ב-main.py
# ============================================================

def main():
    """
    תרחיש ההדגמה המלא: קורא נתונים באופן עצל, בונה אובייקטים,
    מדגים שימוש במבני נתונים ותורים, מפעיל איטרטורים,
    ומטפל בפקודות בעזרת Context Manager.
    """
    print("======================================================")
    print("   הפעלת סימולציה: מערכת TradeInsight Command         ")
    print("======================================================\n")

    # בניית נתיב מוחלט לקובץ ביחס למיקום קובץ הסקריפט הנוכחי
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, "data", "sample_data.jsonl")

    if not os.path.exists(filepath):
        print(f"שגיאה: קובץ הנתונים לא נמצא בנתיב {filepath}")
        print("יש ליצור את הקובץ בעזרת בינה מלאכותית לפי הנחיות שלב ה'.")
        return

    # ==========================================
    # 1. משיכת נתונים באופן עצל (Generator)
    # ==========================================
    print("[1] טעינת נתונים באמצעות גנרטור (Lazy Evaluation):")
    orders_generator = load_orders_from_file(filepath)

    # צריכת הגנרטור לתוך רשימה רק לצורך המשך ההדגמה בסעיפים הבאים
    all_orders = list(orders_generator)
    print(f"נטענו בהצלחה {len(all_orders)} פקודות מסחר מקובץ הנתונים.\n")

    if not all_orders:
        print("לא נטענו נתונים. הסימולציה עוצרת.")
        return

    # ==========================================
    # 2. מודל מונחה עצמים (OOP) והרכבה
    # ==========================================
    print("[2] בניית פלטפורמת המסחר (OOP & Composition):")
    platform = TradingPlatform()

    for order in all_orders:
        try:
            platform.add_order(order)
        except ValueError:
            pass  # דילוג על כפילויות מזהים אם ישנן

    print(f"פלטפורמת המסחר מנהלת כעת {len(platform)} פקודות ייחודיות.")
    print(f"שווי הנפח הכולל במערכת: {platform.get_total_volume():.2f}\n")

    # ==========================================
    # 3. מבני נתונים ותורים (Data Structures)
    # ==========================================
    print("[3] ניתוב פקודות לתורים ייעודיים:")

    regular_processed = process_regular_queue(all_orders)
    print(f" - תור שגרתי (FIFO): טופלו {len(regular_processed)} פקודות רגילות.")

    priority_processed = process_priority_queue(all_orders)
    if priority_processed:
        urgent = priority_processed[0]
        print(f" - תור עדיפויות (Heap): טופלה פקודת חירום {urgent.order_id} בעדיפות {urgent.get_priority()}.")
    print()

    # ==========================================
    # 4. עיבוד אוספים ומיון (Comprehensions & Sorting)
    # ==========================================
    print("[4] עיבוד אוספים (Comprehensions) ומיון מתקדם:")
    large_orders, expensive_symbols, order_values = demonstrate_comprehensions(all_orders)
    print(f" - נמצאו {len(large_orders)} פקודות בנפח גדול (מעל 100 יחידות).")
    print(f" - סמלי מניות יקרות באוסף: {expensive_symbols}")

    by_qty, by_price_desc, by_two_fields = demonstrate_sorting(all_orders)
    print(f" - הפקודה היקרה ביותר (לאחר מיון עולה): מזהה {by_price_desc[0].order_id} במחיר {by_price_desc[0].price}.\n")

    # ==========================================
    # 5. איטרטורים עצמאיים על אותו אוסף
    # ==========================================
    print("[5] מעבר על נתונים עם שני איטרטורים עצמאיים במקביל:")
    collection = OrderCollection()
    for o in all_orders[:3]:
        collection.add_order(o)

    iter1 = iter(collection)
    iter2 = iter(collection)

    print(f" - איטרטור 1, פריט ראשון: {next(iter1).order_id}")
    print(f" - איטרטור 2, פריט ראשון: {next(iter2).order_id}")
    print(f" - איטרטור 1, פריט שני: {next(iter1).order_id}\n")

    # ==========================================
    # 6. צינור עיבוד עצל (Lazy Pipeline)
    # ==========================================
    print("[6] הפעלת צינור עיבוד עצל מרובה שלבים:")
    pipeline = run_lazy_pipeline(all_orders)

    try:
        print(f" - משיכה ראשונה: {next(pipeline)}")
        print(f" - משיכה שנייה: {next(pipeline)}")
        print(" - עוצר צריכה בכוונה כדי להוכיח חיסכון במשאבים (הערכה עצלה).\n")
    except StopIteration:
        print(" - אין מספיק פריטים בצינור העיבוד שמקיימים את התנאים.\n")

    # ==========================================
    # 7. מנהל הקשר מותאם אישית (Context Manager)
    # ==========================================
    print("[7] ניהול הקשר וטיפול בטוח (Context Manager):")
    demo_order = all_orders[0]

    print("--- תרחיש עיבוד תקין ---")
    with OrderProcessingContext(demo_order) as o:
        print(f"מבצע פעולות מסחר על מניית {o.symbol}...")
        # כאן מתבצעת הלוגיקה - ביציאה מהבלוק הסטטוס יתעדכן ל'בוצעה'

    print(f"סטטוס הפקודה לאחר הבלוק: {demo_order.status}\n")

    print("--- תרחיש חריגה (שגיאת רשת) ---")
    # איפוס הסטטוס לצורך ההדגמה
    demo_order.status = "ממתינה"
    try:
        with OrderProcessingContext(demo_order) as o:
            print(f"מתחיל עיבוד של {o.order_id}...")
            raise ConnectionError("נפילת תקשורת פתאומית מול השרת החיצוני!")
    except ConnectionError as e:
        print(f"נלכדה חריגה במערכת: {e}")

    print(f"סטטוס הפקודה לאחר השגיאה (שחזור מצב): {demo_order.status}")

    print(f"\n{'=' * 60}")
    print("|                      סיום תרחיש ההדגמה                   |")
    print('=' * 60)


if __name__ == "__main__":
    main()