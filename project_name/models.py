from abc import ABC, abstractmethod
import time

# ============================================================
#                      סעיפים 1, 3, 4, 5
# ============================================================

class TradeOrder(ABC):
    def __init__(self, order_id: str, symbol: str, action: str, quantity: int, price: float):
        """מאתחל פקודת מסחר עם נתוני בסיס וזמן יצירה."""
        self._quantity = 0
        self._price = 0.0
        self.order_id = order_id
        self.symbol = symbol
        self.action = action
        self.quantity = quantity
        self.price = price
        self.status = "ממתינה"
        self.timestamp = time.time()

    @property
    def quantity(self):
        """החזרת הכמות בקריאה"""
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        """ מוודא שהכמות המוזנת היא מספר שלם וחיובי """
        if not isinstance(value, int) or value <= 0:
            raise ValueError("הכמות חייבת להיות מספר שלם וגדול מאפס")
        self._quantity = value

    @property
    def price(self):
        """ מחזיר את מחיר היעד של הפקודה """
        return self._price

    @price.setter
    def price(self, value):
        """ מוודא שהמחיר המעודכן הוא חיובי ותקין """
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("המחיר חייב להיות מספר חיובי וגדול מאפס.")
        self._price = float(value)

    @abstractmethod
    def get_priority(self) -> int:
        """ מתודה להורשה """
        pass

    def __str__(self):
        """מחזיר ייצוג מילולי קריא של הפקודה למשתמש """
        return f"פקודה {self.order_id}: {self.action} סמל {self.symbol}, כמות {self.quantity}, מחיר {self.price}, מצב {self.status}"

    def __repr__(self):
        """ מחזיר ייצוג טכני של הפקודה לצורכי פיתוח """
        return f"TradeOrder(id={self.order_id}, symbol={self.symbol}, action={self.action}, qty={self.quantity}, price={self.price})"

    def __lt__(self, other):
        """ מגדיר השוואה לפי דחיפות וזמן, לטובת סידור בתור העדיפויות """
        if not isinstance(other, TradeOrder):
            raise TypeError("לא ניתן להשוות בין אובייקטים מסוגים שונים")
        if self.get_priority() == other.get_priority():
            return self.timestamp < other.timestamp
        return self.get_priority() < other.get_priority()

    def __eq__(self, other):
        """ מגדיר שוויון בין פקודות על סמך המזהה הייחודי בלבד """
        if not isinstance(other, TradeOrder):
            return False
        return self.order_id == other.order_id


# ============================================================
# סעיף 3 ו-5 - פולימורפיזם, בנאי אלטרנטיבי וכלים נוספים
# ============================================================

class MarketOrder(TradeOrder):
    def get_priority(self) -> int:
        """ מגדיר עדיפות רגילה (2) לפקודת שוק שגרתית """
        return 2

    @classmethod
    def from_dict(cls, data: dict):
        """ יוצר אובייקט פקודה חדש מתוך מילון נתונים חיצוני """
        try:
            return cls(
                order_id=data["id"],
                symbol=data["symbol"],
                action=data["action"],
                quantity=data["quantity"],
                price=data["price"]
            )
        except KeyError as error:
            raise ValueError("חסרים נתונים חובה ביצירת הפקודה") from error


class StopLossOrder(TradeOrder):
    def __init__(self, order_id: str, symbol: str, action: str, quantity: int, price: float, stop_price: float):
        """ מאתחל פקודת חירום ומוסיף לה מחיר לעצירת-הפסד """
        super().__init__(order_id, symbol, action, quantity, price)
        self.stop_price = stop_price

    def get_priority(self) -> int:
        """ מגדיר עדיפות עליונה (1) לביצוע מיידי של הפקודה """
        return 1


# ============================================================
# סעיף 1 - מחלקות ואחריויות              
# ============================================================

class Portfolio:
    def __init__(self, initial_balance: float):
        """ מאתחל תיק השקעות עם יתרה התחלתית ומלאי ריק """
        self.balance = initial_balance
        self.holdings = {}

    def reserve_funds(self, amount: float) -> bool:
        """ משריין תקציב מקופת התיק ומוודא שהיתרה מספיקה """
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("הסכום חייב להיות חיובי")

        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def release_funds(self, amount: float):
        """ מחזיר לחשבון כסף ששוריין אם הפעולה בוטלה """
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("הסכום חייב להיות חיובי")
        self.balance += amount

    def reserve_stock(self, symbol: str, quantity: int) -> bool:
        """ משריין מניות למכירה ומוודא שיש מספיק במלאי """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("הכמות חייבת להיות מספר שלם חיובי")

        if symbol in self.holdings and self.holdings[symbol] >= quantity:
            self.holdings[symbol] -= quantity
            return True
        return False

    def release_stock(self, symbol: str, quantity: int):
        """ מחזיר מניות למלאי במידה והמכירה לא הושלמה """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("הכמות חייבת להיות מספר שלם חיובי")

        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity

    def add_stock(self, symbol: str, quantity: int):
        """ מוסיף מניות חדשות למלאי לאחר קנייה מוצלחת """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("הכמות חייבת להיות מספר שלם חיובי")

        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity

    def __str__(self):
        "" "מחזיר מחרוזת המציגה את יתרת הכסף ומלאי המניות בתיק """
        return f"יתרה פנויה: {self.balance} | מלאי מניות: {self.holdings}"


# ============================================================
# סעיף 2 ו-5 - הרכבה/הכלה (Composition) וכלים נוספים    
# ============================================================

class TradingPlatform:
    def __init__(self):
        """ מאתחל פלטפורמה שמכילה ומנהלת אוסף פקודות במילון """
        self.orders_collection = {}

    def add_order(self, order: TradeOrder):
        """ מוסיף פקודה חדשה לאוסף ומונע כפילות מזהים """
        if not isinstance(order, TradeOrder):
            raise TypeError("יש להעביר אובייקט פקודת מסחר תקני")

        if order.order_id in self.orders_collection:
            raise ValueError("מזהה הפקודה כבר קיים במערכת")

        self.orders_collection[order.order_id] = order
        return True

    def remove_order(self, order_id: str):
        """ מסיר פקודה מהאוסף בצורה בטוחה לפי מזהה """
        if order_id in self.orders_collection:
            del self.orders_collection[order_id]
            return True
        return False

    def get_total_volume(self) -> float:
        """ מחשב את השווי הכספי הכולל של כל הפקודות באוסף """
        total = 0.0
        for order in self.orders_collection.values():
            total += order.quantity * order.price
        return total

    def __len__(self):
        """ מחזיר את מספר הפקודות הפעילות הקיימות כעת במערכת """
        return len(self.orders_collection)