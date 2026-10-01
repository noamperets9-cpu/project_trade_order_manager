# processing.py
from collections import deque
import heapq
from models import TradeOrder

def process_fifo_queue(orders_list: list):
    # יצירת תור עבודה רגיל עבור פקודות שגרתיות המטופלות לפי סדר הגעה
    work_queue = deque()
    
    # הוספת הפריטים לתור המערכת
    for order in orders_list:
        work_queue.append(order)
        
    processed_orders = []
    # שליפת הפקודות ועיבודן כל עוד התור אינו ריק
    while work_queue:
        current_order = work_queue.popleft()
        current_order.status = "בוצעה"
        processed_orders.append(current_order)
        
    return processed_orders

def process_priority_queue(orders_list: list):
    # ניהול תור עדיפויות שבו פקודות חירום מטופלות לפני פקודות רגילות
    priority_heap = []
    
    # הוספת פריטים לתור העדיפויות 
    # ההשוואה מתבצעת אוטומטית בזכות פונקציית הקסם שהגדרנו במחלקה
    for order in orders_list:
        heapq.heappush(priority_heap, order)
        
    processed_orders = []
    # שליפת הפריט הדחוף ביותר מהתור
    while priority_heap:
        urgent_order = heapq.heappop(priority_heap)
        urgent_order.status = "טופלה בדחיפות"
        processed_orders.append(urgent_order)
        
    return processed_orders

def analyze_orders_data(orders_list: list):
    # שימוש בפירוק ערכים מתוך אוסף נתונים
    if len(orders_list) >= 3:
        first_order, *middle_orders, last_order = orders_list
    
    # שימוש בסט לשמירת ערכים ייחודיים בלבד של סימולי מניות
    unique_symbols = set()
    for order in orders_list:
        unique_symbols.add(order.symbol)
        
    # הדגמת הסרת ערך מהסט תוך שימוש בפונקציה בטוחה
    unique_symbols.discard("UNKNOWN")
    
    # שימוש במילון לקיבוץ וספירת כמות הפקודות לפי מצב נוכחי
    status_counter = {}
    for order in orders_list:
        # שימוש במתודה מובנית למניעת קריסה במקרה של מפתח חסר
        current_count = status_counter.get(order.status, 0)
        status_counter[order.status] = current_count + 1
        
    # הדגמת כתיבה מקוצרת וקריאה ליצירת רשימה מסוננת
    pending_only = [order for order in orders_list if order.status == "ממתינה"]
    
    # יצירת מילון מתקדם למיפוי מהיר בין מזהה הפקודה לאובייקט עצמו
    mapped_orders = {order.order_id: order for order in orders_list}
    
    return unique_symbols, status_counter, pending_only, mapped_orders

def sort_system_orders(orders_list: list):
    # מיון אוסף נתונים באמצעות פונקציה אנונימית לפי מחיר
    sorted_by_price = sorted(orders_list, key=lambda order: order.price)
    
    # פונקציית עזר פנימית למיון מדורג
    def sort_by_symbol_and_qty(order: TradeOrder):
        # המיון מתבצע תחילה לפי שם המניה ולאחר מכן לפי הכמות המבוקשת
        return (order.symbol, order.quantity)
        
    # מיון האוסף באמצעות הפונקציה הרגילה שהוגדרה
    sorted_complex = sorted(orders_list, key=sort_by_symbol_and_qty)
    
    return sorted_by_price, sorted_complex