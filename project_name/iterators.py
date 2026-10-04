from models import TradeOrder


# ============================================================
#        סעיף 1 - Iterable ו-Iterator מותאמים אישית
# ============================================================

class OrderIterator:
    def __init__(self, orders_list: list):
        """ מאתחל את האיטרטור עם אוסף הפקודות וקובע את אינדקס ההתחלה לאפס """
        self._orders = orders_list
        self._index = 0  # שמירת המיקום ההתחלתי

    def __iter__(self):
        """ מחזיר את המופע הנוכחי עצמו כדי לעמוד בפרוטוקול האיטרציה """
        return self

    def __next__(self):
        """ שולף את הפקודה הבאה בתור, או זורק חריגת עצירה בסיום האוסף """
        # 1. בדיקה האם הגענו לסוף האוסף
        if self._index >= len(self._orders):
            # זריקת חריגה מובנית המאותתת ללולאה לעצור
            raise StopIteration

        # 2. שליפת הפריט הנוכחי
        current_order = self._orders[self._index]

        # 3. קידום האינדקס לקראת הפסיעה הבאה
        self._index += 1

        return current_order


class OrderCollection:
    def __init__(self):
        """ מאתחל אוסף ריק המשמש כמסילה (Iterable) לשמירת פקודות המסחר """
        self._orders = []

    def add_order(self, order: TradeOrder):
        """ מוסיף פקודת מסחר חדשה אל תוך רשימת הנתונים באוסף """
        self._orders.append(order)

    def __iter__(self):
        """ מייצר ומחזיר איטרטור (חץ) חדש המאפשר מעבר עצמאי על האוסף """
        return OrderIterator(self._orders)


# ============================================================
#                 סעיף 2 - Generator עם yield
# ============================================================

def filter_urgent_orders(orders: list):
    """ מחולל המשהה את הריצה ומחזיר בהדרגה רק פקודות בעלות עדיפות עליונה """
    for order in orders:
        if order.get_priority() == 1:  # תנאי עסקי: פקודות חירום (Stop-Loss)
            # הפקודה yield מקפיאה את הריצה ומחזירה את האיבר החוצה
            yield order


# ============================================================
#       סעיף 3 - Generator Expression וצינור עיבוד עצל
# ============================================================

def run_lazy_pipeline(orders: list):
    """ מפעיל צינור עיבוד תלת-שלבי המסנן וממיר פקודות ללא העמסת זיכרון """

    # שלב 1: סינון ראשוני - רק פקודות בסטטוס "ממתינה"
    pending_orders = (order for order in orders if order.status == "ממתינה")

    # שלב 2: סינון נוסף - רק פקודות שסך הכמות שלהן גדול מ-50
    large_pending_orders = (order for order in pending_orders if order.quantity > 50)

    # שלב 3: המרה/חילוץ - חילוץ מזהה הפקודה וחישוב שווי העסקה, והחזרת מחרוזת מסכמת
    pipeline_results = (f"Order ID: {order.order_id} | Total Value: {order.quantity * order.price}"
                        for order in large_pending_orders)

    return pipeline_results