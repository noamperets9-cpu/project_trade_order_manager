from abc import ABC, abstractmethod
import time

class TradeOrder(ABC):
    # מחלקת בסיס אבסטרקטית המייצגת פקודת מסחר גנרית בארגון
    def __init__(self, order_id: str, symbol: str, action: str, quantity: int, price: float):
        self._quantity = 0
        self._price = 0.0
        self.order_id = order_id
        self.symbol = symbol
        self.action = action  # הוספנו את סוג הפעולה (Buy / Sell)
        self.quantity = quantity
        self.price = price
        self.status = "ממתינה"
        self.timestamp = time.time()

    @property
    def quantity(self):
        # חשיפת הכמות בצורה בטוחה 
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        # מנגנון אימות שמונע הזנת כמות שלילית או אפס וזורק שגיאה מתאימה
        if not isinstance(value, int) or value <= 0:
            raise ValueError("כמות המניות חייבת להיות מספר שלם וגדול מאפס.")
        self._quantity = value

    @property
    def price(self):
        # חשיפת המחיר בצורה בטוחה
        return self._price

    @price.setter
    def price(self, value):
        # מנגנון אימות שמונע הזנת מחיר שלילי או אפס וזורק שגיאה מתאימה
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("המחיר חייב להיות מספר חיובי וגדול מאפס.")
        self._price = float(value)

    @abstractmethod
    def get_priority(self) -> int:
        # מתודה אבסטרקטית שמחייבת את כל המחלקות היורשות להגדיר עדיפות בתור
        pass

    def __str__(self):
        # ייצוג ידידותי למשתמש הקצה
        return f"פקודה {self.order_id}: {self.action} סמל {self.symbol}, כמות {self.quantity}, מחיר {self.price}, מצב {self.status}"

    def __repr__(self):
        # ייצוג למפתחים לצורכי דיבאג 
        return f"TradeOrder(id={self.order_id}, symbol={self.symbol}, action={self.action}, qty={self.quantity}, price={self.price})"

    def __lt__(self, other):
        # פונקציית קסם קריטית עבור תור העדיפויות בשלב הבא
        # מספר קטן יותר משמעותו עדיפות גבוהה יותר בטיפול
        if self.get_priority() == other.get_priority():
            return self.timestamp < other.timestamp
        return self.get_priority() < other.get_priority()

class MarketOrder(TradeOrder):
    # מחלקה יורשת המייצגת פקודת מסחר שגרתית 
    def get_priority(self) -> int:
        # פקודה שגרתית מקבלת עדיפות רגילה
        return 2 

    @classmethod
    def from_dict(cls, data: dict):
        # בנאי אלטרנטיבי ליצירת אובייקט מתוך מילון נתונים 
        try:
            return cls(
                order_id=data["id"],
                symbol=data["symbol"],
                action=data["action"],  # תמיכה בסוג הפעולה מהמילון
                quantity=data["quantity"],
                price=data["price"]
            )
        except KeyError as error:
            raise ValueError("חסרים נתונים חובה ביצירת הפקודה.") from error

class StopLossOrder(TradeOrder):
    # מחלקה יורשת המייצגת פקודת מסחר דחופה שמופעלת בתנאי חירום 
    def __init__(self, order_id: str, symbol: str, action: str, quantity: int, price: float, stop_price: float):
        super().__init__(order_id, symbol, action, quantity, price)
        self.stop_price = stop_price

    def get_priority(self) -> int:
        # פקודת חירום מקבלת עדיפות עליונה בטיפול
        return 1

class Portfolio:
    # מחלקת משאבים המייצגת את חשבון ההחזקות בארגון
    def __init__(self, initial_balance: float):
        self.balance = initial_balance  # יתרת הכסף הפנוי בחשבון
        self.holdings = {}              # מילון לניהול מלאי המניות (מפתח: סמל מניה, ערך: כמות)

    def reserve_funds(self, amount: float) -> bool:
        # שריון משאבים (תקציב) עבור פקודת קנייה
        # בודק אם יש מספיק כסף, מוריד מהיתרה ומחזיר True לאישור, או False לסירוב
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def release_funds(self, amount: float):
        # שחרור כספים חזרה לתיק במקרה שפקודת הקנייה מבוטלת או נכשלת
        self.balance += amount

    def reserve_stock(self, symbol: str, quantity: int) -> bool:
        # שריון משאבים (מלאי) עבור פקודת מכירה
        # בודק אם המניה קיימת בתיק ואם יש מספיק כמות ממנה
        if symbol in self.holdings and self.holdings[symbol] >= quantity:
            self.holdings[symbol] -= quantity
            return True
        return False

    def release_stock(self, symbol: str, quantity: int):
        # שחרור מניות חזרה למלאי במקרה שפקודת המכירה מבוטלת או נכשלת
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity

    def add_stock(self, symbol: str, quantity: int):
        # עדכון סופי של המלאי לאחר פקודת קנייה שבוצעה בהצלחה
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
            
    def __str__(self):
        # ייצוג ידידותי להצגת מצב התיק הנוכחי בדוחות
        return f"יתרה פנויה: {self.balance} | מלאי מניות: {self.holdings}"

class TradingPlatform:
    # מחלקה המדגימה קשר של הכלה ומנהלת את אוסף הפקודות בארגון
    def __init__(self):
        # שימוש במילון כדי לאתר פקודות במהירות לפי מזהה ייחודי
        self.orders_collection = {}

    def add_order(self, order: TradeOrder):
        # הוספת פקודה לאוסף תוך טיפול במקרה של כפילות 
        if order.order_id in self.orders_collection:
            raise ValueError("מזהה הפקודה כבר קיים במערכת.")
        self.orders_collection[order.order_id] = order
        return True

    def remove_order(self, order_id: str):
        # מחיקת פקודה מהאוסף בצורה בטוחה
        if order_id in self.orders_collection:
            del self.orders_collection[order_id]
            return True
        return False

    def get_total_volume(self) -> float:
        # פעולת עזר המחשבת נתון מסכם של כלל הפקודות באוסף
        total = 0.0
        for order in self.orders_collection.values():
            total += order.quantity * order.price
        return total