# processing.py
from models import TradeOrder
from collections import deque
import heapq

# ==========================================
# 1. רשימות (list) וטופלים (tuple) - פריקת ערכים
# ==========================================
def process_order_batch(batch_name: str, *orders):
    """
    מקבלת פקודות, מדגימה שימוש בטופל (tuple), רשימה (list) ופריקה (unpacking) באמצעות כוכבית.
    """
    if not orders:
        return None
    
    # שימוש ב-* כדי לאסוף את הערכים שנותרו (Unpacking)
    first_order, *remaining_orders = orders
    
    # שימוש ב-tuple עבור רשומה קצרה וקבועה (שם האצווה, כמות כוללת, והפקודה הראשונה)
    batch_summary = (batch_name, len(orders), first_order)
    
    # שימוש ב-list עבור אוסף מסודר שניתן לשינוי
    working_list = list(remaining_orders)
    working_list.append(first_order)
    
    return batch_summary, working_list

# ==========================================
# 2. קבוצות (set) לערכים ייחודיים
# ==========================================
def manage_active_symbols(orders_list: list):
    """
    מפיקה קבוצה של סמלי המניות הפעילים ומדגימה פעולות על set.
    """
    active_symbols = set()
    
    for order in orders_list:
        # 1. הוספת איבר לקבוצה (add)
        active_symbols.add(order.symbol)
        
    # 2. בדיקת השתייכות באמצעות in
    if "AAPL" in active_symbols:
        print("שים לב: מניית אפל קיימת באוסף הפקודות.")
        
    # 3. מחיקה זהירה באמצעות discard (שלא קורסת אם האיבר לא קיים, בניגוד ל-remove)
    active_symbols.discard("UNKNOWN_SYMBOL")
    
    return active_symbols

# ==========================================
# 3. מילונים (dict) לאיתור וקיבוץ
# ==========================================
def build_order_dictionaries(orders_list: list):
    """
    יוצרת שני מילונים: אחד לאיתור לפי מזהה, והשני לספירת כמות הפקודות לכל מניה.
    """
    # מילון 1: לאיתור אובייקט לפי מזהה ייחודי
    orders_by_id = {}
    for order in orders_list:
        # החלטה מפורשת: אם המזהה כבר קיים, נדלג ולא נדרוס
        if order.order_id in orders_by_id:
            print(f"אזהרה: הפקודה {order.order_id} כבר קיימת. מדלג.")
        else:
            orders_by_id[order.order_id] = order
            
    # מילון 2: לספירה (כמה פקודות יש לכל סמל מניה)
    symbol_counts = {}
    for order in orders_list:
        # שימוש ב-get כדי לשלוף ערך או לתת 0 כברירת מחדל אם המפתח לא קיים
        current_count = symbol_counts.get(order.symbol, 0)
        symbol_counts[order.symbol] = current_count + 1
        
    # הדגמת מעבר על המילון עם items() ו-unpacking
    print("\n--- סיכום פקודות לפי מניה ---")
    for symbol, count in symbol_counts.items():
        print(f"מניית {symbol}: {count} פקודות")
        
    return orders_by_id, symbol_counts
# ==========================================
# 4. תור FIFO באמצעות deque
# ==========================================
def process_regular_queue(orders_list: list):
    """
    תור עבור תהליך שמטפל בפקודות מסחר לפי סדר הגעתן (FIFO).
    הסבר עסקי: סדר ההגעה חשוב בפקודות שגרתיות כדי לשמור על הוגנות תפעולית 
    (הראשון שמבקש הוא הראשון שמקבל מענה) ולמנוע מצב שבו פקודות ישנות נדחקות לאחור.
    """
    regular_queue = deque()
    
    # הוספת לפחות שלושה פריטים באמצעות append
    for order in orders_list[:4]:
        regular_queue.append(order)
        
    processed_orders = []
    
    # הוצאת פריטים באמצעות popleft וטיפול זהיר בתור ריק ללא קריסה
    while True:
        try:
            next_order = regular_queue.popleft()
            processed_orders.append(next_order)
        except IndexError:
            print("התור השגרתי התרוקן. אין פקודות נוספות לביצוע כרגע.")
            break
            
    return processed_orders

# ==========================================
# 5. תור עדיפויות באמצעות heapq
# ==========================================
def process_priority_queue(orders_list: list):
    """
    תור עדיפויות לפקודות שבהן הדחיפות (למשל Stop-Loss) קודמת לזמן ההגעה.
    הגדרה: מספר קטן יותר במתודת get_priority (למשל 1 מול 2) מציין עדיפות גבוהה יותר בטיפול.
    """
    priority_queue = []
    
    # הוספת פריטים בעלי עדיפויות שונות. heapq משתמש בפונקציית __lt__ שהגדרנו.
    for order in orders_list:
        heapq.heappush(priority_queue, order)
        
    processed_priority = []
    
    # הרשימה הפנימית priority_queue אינה ממוינת במלואה ברקע, 
    # אבל heappop תמיד מבטיחה את שליפת הפריט בעל העדיפות העליונה באותו רגע.
    if priority_queue:
        urgent_order = heapq.heappop(priority_queue)
        processed_priority.append(urgent_order)
        
    return processed_priority

# ==========================================
# 6. Comprehensions
# ==========================================
def demonstrate_comprehensions(orders_list: list):
    """
    הדגמת שימוש ב-Comprehensions לסינון, מיפוי ויצירת מבנים קצרים וקריאים.
    """
    # List Comprehension: סינון - רק פקודות עם כמות גדולה מ-100
    large_orders = [order for order in orders_list if order.quantity > 100]
    
    # Set Comprehension: הפקת ערכים ייחודיים - סמלי מניות שנסחרים במחיר גבוה מ-500
    expensive_symbols = {order.symbol for order in orders_list if order.price > 500}
    
    # Dict Comprehension: יצירת מיפוי בין מזהה הפקודה לשווי הכולל שלה
    order_values = {order.order_id: (order.quantity * order.price) for order in orders_list}
    
    return large_orders, expensive_symbols, order_values

# ==========================================
# 7. מיון ופונקציות כערכים
# ==========================================
def extract_quantity(order: TradeOrder):
    # פונקציה רגילה שתשמש כ-key למיון
    return order.quantity

def demonstrate_sorting(orders_list: list):
    """
    הדגמת מיון אוספים בצורות שונות באמצעות sorted.
    """
    # 1. מיון באמצעות פונקציה רגילה כ-key (סדר עולה של כמות)
    sorted_by_qty = sorted(orders_list, key=extract_quantity)
    
    # 2. מיון באמצעות lambda כ-key (סדר יורד של מחיר)
    sorted_by_price_desc = sorted(orders_list, key=lambda o: o.price, reverse=True)
    
    # 3. מיון לפי שני שדות באמצעות tuple: קודם לפי סטטוס ואז לפי מחיר (יורד)
    sorted_by_two_fields = sorted(orders_list, key=lambda o: (o.status, -o.price))
    
    return sorted_by_qty, sorted_by_price_desc, sorted_by_two_fields