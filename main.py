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
from models import Portfolio
from strategies import FullBalancePolicy, RiskLimitPolicy
from services import OrderApprovalService
import console_ui as ui

# שער להדגמה ללא רשת. החיבור לשירות האמיתי (סעיף 2) יחליף את הפונקציה הזו
DEMO_USD_ILS_RATE = 3.70
DEMO_BUDGET_ILS = 600_000


def demo_rate_provider() -> float:
    """ מקור שער מדומה להרצה ללא רשת """
    return DEMO_USD_ILS_RATE


def order_type_label(order) -> str:
    """ תווית צבעונית לסוג הפקודה, לפי העדיפות שלה (פולימורפיזם) """
    if order.get_priority() == 1:
        return ui.paint("Stop-Loss", ui.RED, ui.BOLD)
    return "Market"


def side_label(order) -> str:
    """ קנייה בירוק, מכירה באדום """
    color = ui.GREEN if order.action.lower() == "buy" else ui.RED
    return ui.paint(order.action, color)


def status_label(status: str) -> str:
    colors = {"ממתינה": ui.YELLOW, "בטיפול": ui.BLUE, "בוצעה": ui.GREEN}
    return ui.paint(status, colors.get(status, ui.RESET), ui.BOLD)


def decision_label(result) -> str:
    if result.approved:
        return ui.paint("✔ approved", ui.GREEN)
    return ui.paint("✘ rejected", ui.RED)


# ============================================================
#                 חלק ה' - תרחיש ההדגמה ב-main.py
# ============================================================

def main():
    """
    תרחיש ההדגמה המלא: קורא נתונים באופן עצל, בונה אובייקטים,
    מדגים שימוש במבני נתונים ותורים, מפעיל איטרטורים,
    ומטפל בפקודות בעזרת Context Manager.
    """
    ui.banner("TradeInsight Command", "סימולציה של מערכת לניתוב ובקרת פקודות מסחר")

    # בניית נתיב מוחלט לקובץ ביחס למיקום קובץ הסקריפט הנוכחי
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, "data", "sample_data.jsonl")

    if not os.path.exists(filepath):
        ui.error(f"קובץ הנתונים לא נמצא: {filepath}")
        return

    # ==========================================
    # 1. משיכת נתונים באופן עצל (Generator)
    # ==========================================
    ui.section(1, "טעינת פקודות מהקובץ", "Generator")
    orders_generator = load_orders_from_file(filepath)

    # צריכת הגנרטור לתוך רשימה רק לצורך המשך ההדגמה בסעיפים הבאים
    all_orders = list(orders_generator)

    if not all_orders:
        ui.error("לא נטענו נתונים. הסימולציה עוצרת.")
        return

    ui.ok(f"נטענו {len(all_orders)} פקודות מסחר")
    print()
    ui.table(
        ["ID", "Symbol", "Side", "Qty", "Price", "Type"],
        [[o.order_id, o.symbol, side_label(o), o.quantity, ui.usd(o.price), order_type_label(o)]
         for o in all_orders],
        align="lllrrl",
    )

    # ==========================================
    # 2. מודל מונחה עצמים (OOP) והרכבה
    # ==========================================
    ui.section(2, "פלטפורמת המסחר", "OOP & Composition")
    platform = TradingPlatform()

    for order in all_orders:
        try:
            platform.add_order(order)
        except ValueError:
            pass  # דילוג על כפילויות מזהים אם ישנן

    ui.kv("פקודות ייחודיות בפלטפורמה", len(platform))
    ui.kv("שווי כולל של כל הפקודות", ui.usd(platform.get_total_volume()))

    # ==========================================
    # 3. מבני נתונים ותורים (Data Structures)
    # ==========================================
    ui.section(3, "ניתוב פקודות לתורים", "deque & heapq")

    regular_processed = process_regular_queue(all_orders)
    ui.info(f"תור רגיל (FIFO) - טופלו {len(regular_processed)} פקודות לפי סדר הגעה:")
    ui.note("  →  ".join(o.order_id for o in regular_processed))

    priority_processed = process_priority_queue(all_orders)
    if priority_processed:
        urgent = priority_processed[0]
        ui.info("תור עדיפויות (Heap) - הפקודה הדחופה ביותר נשלפה ראשונה:")
        ui.note(f"{urgent.order_id} ({urgent.symbol}) | priority {urgent.get_priority()}")

    # ==========================================
    # 4. עיבוד אוספים ומיון (Comprehensions & Sorting)
    # ==========================================
    ui.section(4, "סינון ומיון", "Comprehensions & sorted")
    large_orders, expensive_symbols, order_values = demonstrate_comprehensions(all_orders)
    by_qty, by_price_desc, by_two_fields = demonstrate_sorting(all_orders)

    ui.kv("פקודות בנפח גדול (מעל 100 יחידות)", len(large_orders))
    ui.kv("מניות יקרות (מעל $500)", ", ".join(sorted(expensive_symbols)))
    top = by_price_desc[0]
    ui.kv("הפקודה היקרה ביותר (מיון יורד לפי מחיר)", f"{top.order_id} {ui.usd(top.price)}")

    # ==========================================
    # 5. איטרטורים עצמאיים על אותו אוסף
    # ==========================================
    ui.section(5, "שני איטרטורים על אותו אוסף", "Iterator")
    collection = OrderCollection()
    for o in all_orders[:3]:
        collection.add_order(o)

    iter1 = iter(collection)
    iter2 = iter(collection)

    ui.info(f"iter1 → {next(iter1).order_id}")
    ui.info(f"iter2 → {next(iter2).order_id}")
    ui.info(f"iter1 → {next(iter1).order_id}")
    ui.note("כל איטרטור זוכר את המיקום שלו בנפרד")

    # ==========================================
    # 6. צינור עיבוד עצל (Lazy Pipeline)
    # ==========================================
    ui.section(6, "צינור עיבוד עצל", "Lazy Pipeline")
    pipeline = run_lazy_pipeline(all_orders)

    try:
        ui.info(f"משיכה 1: {next(pipeline)}")
        ui.info(f"משיכה 2: {next(pipeline)}")
        ui.note("שאר הפריטים לא חושבו כלל - הם יחושבו רק כשיבקשו אותם")
    except StopIteration:
        ui.warn("אין מספיק פריטים בצינור שעומדים בתנאים")

    # ==========================================
    # 7. מנהל הקשר מותאם אישית (Context Manager)
    # ==========================================
    ui.section(7, "טיפול בטוח בפקודה", "Context Manager")
    demo_order = all_orders[0]

    ui.subheading("תרחיש תקין")
    before = demo_order.status
    with OrderProcessingContext(demo_order) as o:
        during = o.status
        # כאן מתבצעת הלוגיקה - ביציאה מהבלוק הסטטוס יתעדכן ל'בוצעה'
    ui.info(f"{demo_order.order_id}:  {status_label(before)} → {status_label(during)} → {status_label(demo_order.status)}")

    ui.subheading("תרחיש שגיאת רשת")
    # איפוס הסטטוס לצורך ההדגמה
    demo_order.status = "ממתינה"
    try:
        with OrderProcessingContext(demo_order) as o:
            raise ConnectionError("נפילת תקשורת מול השרת החיצוני")
    except ConnectionError as e:
        ui.error(f"נלכדה חריגה: {e}")

    ui.ok(f"הסטטוס שוחזר אוטומטית: {status_label(demo_order.status)}")

    # ==========================================
    # 8. שלב 2 - Factory ו-Strategy בבקרת תקציב
    # ==========================================
    ui.section(8, "בקרת תקציב בשקלים", "Factory & Strategy")
    stop_loss_count = sum(1 for o in all_orders if o.get_priority() == 1)
    ui.kv("ה-Factory יצר פקודות Stop-Loss", stop_loss_count)
    ui.kv("ה-Factory יצר פקודות שוק", len(all_orders) - stop_loss_count)
    ui.kv("שער דולר-שקל", f"{DEMO_USD_ILS_RATE} {ui.tag_simulated()}")
    ui.kv("תקציב התחלתי", ui.ils(DEMO_BUDGET_ILS))

    buy_orders = [o for o in all_orders if o.action.lower() == "buy"]
    policies = [FullBalancePolicy(), RiskLimitPolicy(max_share=0.25)]
    results_by_policy = []
    portfolios = []

    for policy in policies:
        portfolio = Portfolio(initial_balance=DEMO_BUDGET_ILS)
        service = OrderApprovalService(portfolio, policy, demo_rate_provider)
        results_by_policy.append(service.review_orders(buy_orders))
        portfolios.append(portfolio)

    print()
    ui.table(
        ["ID", "Symbol", "Cost (ILS)", "Full balance", "Risk limit 25%"],
        [[order.order_id, order.symbol, ui.ils(full.cost_ils), decision_label(full), decision_label(risk)]
         for order, full, risk in zip(buy_orders, *results_by_policy)],
        align="llrll",
    )

    ui.subheading("סיכום לפי מדיניות")
    for policy, results, portfolio in zip(policies, results_by_policy, portfolios):
        approved = sum(1 for r in results if r.approved)
        ui.info(f"{policy.name}")
        ui.note(f"approved {approved}/{len(results)} | left {ui.ils(portfolio.balance)}")

    ui.footer("סיום תרחיש ההדגמה")


if __name__ == "__main__":
    main()
