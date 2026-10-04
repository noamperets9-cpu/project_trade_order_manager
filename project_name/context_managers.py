import time
from models import TradeOrder

# ============================================================
#                 סעיף 5 - Context Manager מותאם אישית
# ============================================================

class OrderProcessingContext:
    def __init__(self, order: TradeOrder):
        """ מאתחל את שומר ההקשר עם הפקודה לטיפול """
        self.order = order
        self.previous_status = None
        self.start_time = None

    def __enter__(self):
        """ שומר את הסטטוס הקודם של הפקודה ומשנה אותו זמנית ל'בטיפול' """
        self.previous_status = self.order.status
        self.start_time = time.time()
        self.order.status = "בטיפול"

        return self.order

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ מחזיר את הסטטוס לקדמותו אם הייתה שגיאה, אחרת מעדכן ל'בוצעה' """
        if exc_type is not None:
            self.order.status = self.previous_status
        else:
            self.order.status = "בוצעה"