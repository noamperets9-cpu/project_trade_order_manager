# context_managers.py
import time
from models import TradeOrder

class OrderProcessingContext:
    """
    Context Manager לטיפול בטוח בפקודת מסחר.
    משנה את סטטוס הפקודה ל-'בטיפול' בכניסה.
    ביציאה תקינה משנה ל-'בוצעה'. 
    במקרה של חריגה, מחזיר את הפקודה לסטטוס הקודם שלה.
    """
    def __init__(self, order: TradeOrder):
        self.order = order
        self.previous_status = None
        self.start_time = None

    def __enter__(self):
        # שמירת המצב הקודם לפני השינוי
        self.previous_status = self.order.status
        self.start_time = time.time()
        
        # שינוי סטטוס זמני
        self.order.status = "בטיפול"
        print(f"\n[Context Manager] מתחיל עיבוד של פקודה {self.order.order_id}...")
        
        return self.order

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        
        if exc_type is not None:
            # התרחשה שגיאה בתוך בלוק ה-with. שחזור המצב הקודם.
            self.order.status = self.previous_status
            print(f"[Context Manager] שגיאה זוהתה במהלך הטיפול: {exc_val}")
            print(f"[Context Manager] שחזור מערכות: הפקודה {self.order.order_id} הוחזרה לסטטוס '{self.order.status}'.")
            # אנחנו לא מחזירים True כדי לא להסתיר את החריגה, כנדרש בהוראות
        else:
            # הכל עבר בהצלחה
            self.order.status = "בוצעה"
            print(f"[Context Manager] העיבוד הסתיים בהצלחה. סטטוס עודכן ל-'בוצעה'. זמן ריצה: {execution_time:.4f} שניות.")