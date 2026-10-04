from models import TradeOrder
from collections import deque
import heapq

# ============================================================
#                 סעיף 1 - list ו-tuple
# ============================================================

def process_order_batch(batch_name: str, *orders):
    """
    מדגים פריקת ערכים, שימוש בטופל לרשומה קבועה וברשימה לאוסף הניתן לעריכה
    """
    if not orders:
        raise ValueError("לא התקבלו פקודות לעיבוד.")

    # חילוץ האיבר הראשון והשארת שאר האיברים ברשימה נפרדת
    first_order, *remaining_orders = orders

    # יצירת רשומה קבועה שאינה ניתנת לשינוי כלל
    batch_summary = (batch_name, len(orders), first_order)

    # המרת שאר הפקודות לרשימה מסודרת הניתנת לעריכה
    working_list = list(remaining_orders)

    # הוספת האיבר הראשון לסוף הרשימה החדשה במערך
    working_list.append(first_order)

    return batch_summary, working_list

# ============================================================
#                       סעיף 2 - set
# ============================================================

def manage_active_symbols(orders_list: list):
    """
    שומר סמלי מניות ייחודיים בקבוצה ומדגים פעולות הוספה והסרה בטוחות
    """
    # אתחול קבוצה ריקה לשמירת סמלים ייחודיים בלבד
    active_symbols = set()

    # מעבר על כל הפקודות ברשימה שהתקבלה מהמשתמש
    for order in orders_list:
        # הוספת כל סמל לקבוצה תוך סינון כפילויות אוטומטי
        active_symbols.add(order.symbol)

    # הסרת סמל לא מוכר במידה וקיים ללא קריסת המערכת השלמה
    active_symbols.discard("UNKNOWN_SYMBOL")

    return active_symbols

# ============================================================
#                      סעיף 3 - dict
# ============================================================

def build_order_dictionaries(orders_list: list):
    """
    יוצר מילונים לאיתור פקודות לפי מזהה ולספירת כמויות תוך שימוש בטוח ב-get
    """
    # יצירת מילון לאיתור פקודות לפי מזהה ייחודי מסודר
    orders_by_id = {}

    # מעבר על רשימת הפקודות לאכלוס המילון הראשון
    for order in orders_list:
        # הוספה רק אם המפתח טרם קיים במילון הנתונים
        if order.order_id not in orders_by_id:
            orders_by_id[order.order_id] = order

    # יצירת מילון שני לספירת כמות הפקודות עבור כל חברה
    symbol_counts = {}

    # אכלוס המילון השני תוך מניעת שגיאות של מפתח חסר
    for order in orders_list:
        # משיכת הערך הקיים או מתן ערך התחלתי אפס במידה וחסר במילון
        current_count = symbol_counts.get(order.symbol, 0)

        # עדכון מונה הפקודות עבור המניה הנוכחית בתוספת אחת
        symbol_counts[order.symbol] = current_count + 1

    return orders_by_id, symbol_counts

# ============================================================
#                 סעיף 4 - תור FIFO באמצעות deque
# ============================================================

def process_regular_queue(orders_list: list):
    """ מנהל תור עבודה שגרתי ושולף איברים בצורה בטוחה עד להתרוקנותו """
    # יצירת תור רגיל המטפל בפקודות לפי סדר הגעתן למערכת
    regular_queue = deque()

    # הוספת ארבע הפקודות הראשונות אל סוף התור למטרת בדיקה
    for order in orders_list[:4]:
        regular_queue.append(order)

    # אתחול רשימה שתכיל את הפקודות שטופלו בהצלחה רבה
    processed_orders = []

    # משיכת נתונים מהתור עד להתרוקנותו המלאה ללא הפסקת ריצה
    while True:
        try:
            # הוצאת הפריט הראשון שנכנס אל התור כעת
            next_order = regular_queue.popleft()

            # רישום הפריט שהוצא כחלק מהפקודות שטופלו
            processed_orders.append(next_order)
        except IndexError:
            # עצירת הלולאה כאשר התור מתרוקן מפריטים
            break

    return processed_orders

# ============================================================
#                 סעיף 5 - תור עדיפויות באמצעות heapq
# ============================================================

def process_priority_queue(orders_list: list):
    """ מנהל תור עדיפויות כך שפקודות דחופות נשלפות ראשונות באמצעות heapq """
    # יצירת תור עדיפויות בו פקודות דחופות יקבלו קדימות מיידית
    priority_queue = []

    # הכנסת כלל הפקודות אל התור תוך התבססות על מתודת ההשוואה
    for order in orders_list:
        # דחיפת פריט אל תור העדיפויות באופן מובנה ומהיר
        heapq.heappush(priority_queue, order)

    # אתחול רשימה ייעודית לפקודות שבוצעו בעדיפות
    processed_priority = []

    # בדיקה מוודאת כי התור איננו ריק בטרם שליפת הנתון
    if priority_queue:
        # משיכת הפריט בעל העדיפות הגבוהה ביותר באותו רגע
        urgent_order = heapq.heappop(priority_queue)

        # תוספת הפריט אל רשימת הפקודות שטופלו בהצלחה
        processed_priority.append(urgent_order)

    return processed_priority

# ============================================================
#                   סעיף 6 - Comprehensions
# ============================================================

def demonstrate_comprehensions(orders_list: list):
    """
    מייצר אוספים מסוננים ומומרים בצורה מקוצרת באמצעות List, Set ו-Dict Comprehensions
    """
    # יצירת רשימה מסוננת המכילה רק פקודות בעלות נפח עצום
    large_orders = [order for order in orders_list if order.quantity > 100]

    # יצירת קבוצה המכילה סמלי מניות יקרות ללא כפילות במערכת
    expensive_symbols = {order.symbol for order in orders_list if order.price > 500}

    # בניית מילון הממפה בין המזהה לבין השווי הכולל המחושב
    order_values = {order.order_id: (order.quantity * order.price) for order in orders_list}

    return large_orders, expensive_symbols, order_values

# ============================================================
#                 סעיף 7 - מיון ופונקציות כערכים
# ============================================================

def extract_quantity(order: TradeOrder):
    """
    פונקציית עזר פשוטה המשמשת כמפתח למיון פקודות לפי כמות
    """
    # פונקציית עזר בסיסית המחלצת את נתון הכמות מתוך האובייקט
    return order.quantity


def demonstrate_sorting(orders_list: list):
    """
    ממיין אוספים בדרכים שונות באמצעות פונקציה רגילה, למבדא (lambda) ומיון משולב מרובה שדות
    """
    # מיון הפקודות בסדר עולה לפי כמות בעזרת פונקציית עזר חיצונית
    sorted_by_qty = sorted(orders_list, key=extract_quantity)

    # מיון הפקודות בסדר יורד לפי מחיר בעזרת פונקציה אנונימית מהירה
    sorted_by_price_desc = sorted(orders_list, key=lambda o: o.price, reverse=True)

    # מיון הפקודות לפי שילוב של סטטוס ואז מחיר יורד ברשימה
    sorted_by_two_fields = sorted(orders_list, key=lambda o: (o.status, -o.price))

    return sorted_by_qty, sorted_by_price_desc, sorted_by_two_fields