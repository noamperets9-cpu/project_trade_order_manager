<<<<<<< HEAD
=======
# models.py
>>>>>>> 21545bdd1f760e0b30af4106f8ab1b65b0d2f45c
from abc import ABC, abstractmethod
import time

class TradeOrder(ABC):
    # מחלקת בסיס אבסטרקטית המייצגת פקודת מסחר גנרית בארגון
    def __init__(self, order_id: str, symbol: str, quantity: int, price: float):
        self.order_id = order_id
        self.symbol = symbol
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

<<<<<<< HEAD
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

=======
>>>>>>> 21545bdd1f760e0b30af4106f8ab1b65b0d2f45c
    @abstractmethod
    def get_priority(self) -> int:
        # מתודה אבסטרקטית שמחייבת את כל המחלקות היורשות להגדיר עדיפות בתור
        pass

    def __str__(self):
        # ייצוג ידידותי למשתמש הקצה
<<<<<<< HEAD
        return f"פקודה {self.order_id}: סמל {self.symbol}, כמות {self.quantity}, מחיר {self.price}, מצב {self.status}"
=======
        return f"פקודה {self.order_id}: סמל {self.symbol}, כמות {self.quantity}, מצב {self.status}"
>>>>>>> 21545bdd1f760e0b30af4106f8ab1b65b0d2f45c

    def __repr__(self):
        # ייצוג למפתחים לצורכי דיבאג 
        return f"TradeOrder(id={self.order_id}, symbol={self.symbol}, qty={self.quantity}, price={self.price})"

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
                quantity=data["quantity"],
                price=data["price"]
            )
        except KeyError as error:
            raise ValueError("חסרים נתונים חובה ביצירת הפקודה.") from error

class StopLossOrder(TradeOrder):
    # מחלקה יורשת המייצגת פקודת מסחר דחופה שמופעלת בתנאי חירום 
    def __init__(self, order_id: str, symbol: str, quantity: int, price: float, stop_price: float):
        super().__init__(order_id, symbol, quantity, price)
        self.stop_price = stop_price

    def get_priority(self) -> int:
        # פקודת חירום מקבלת עדיפות עליונה בטיפול
        return 1

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
<<<<<<< HEAD
        return total
=======
        return total
>>>>>>> 21545bdd1f760e0b30af4106f8ab1b65b0d2f45c
