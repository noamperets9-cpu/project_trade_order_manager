import threading
import time
from .models import Portfolio

# ============================================================
#          שלב 2, סעיף 5.2 - Threads ומשאב משותף (יתרת התיק)
# ============================================================
# כמה סוחרים מבקשים לשריין תקציב מאותה יתרה באותו זמן.
# בלי נעילה עלול לקרות הסדר הבא:
#   1. Thread A בודק: היתרה (5,000) מספיקה ל-3,000
#   2. Thread B בודק לפני ש-A הוריד: היתרה עדיין 5,000, מספיקה
#   3. A מוריד -> 2,000
#   4. B מוריד -> 1,000- (שני אישורים, יתרה שלילית)
# ה-Lock עוטף יחד את הבדיקה ואת ההורדה, כך שרק Thread אחד מבצע את הרצף בכל רגע.


class SafePortfolioManager:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self._lock = threading.Lock()
        self.successful_reservations = 0

    def attempt_reservation(self, amount: float) -> bool:
        """
        ניסיון שריון מהקופה המשותפת תוך הגנה עם Lock.
        מחזיר True אם השריון אושר, ו-False אם אין מספיק יתרה.
        """
        with self._lock:
            if self.portfolio.balance < amount:
                return False
            time.sleep(0.01)  # סימולציה לעיבוד כדי להבליט את הצורך בנעילה (אין קריאת רשת בקטע הנעול)
            self.portfolio.reserve_funds(amount)
            self.successful_reservations += 1
            return True


def run_concurrent_reservations(manager: SafePortfolioManager, amounts: list) -> list:
    """
    מפעיל Thread לכל בקשת שריון: קודם מפעילים את כולם (start), ורק אז ממתינים לסיומם (join).
    מחזיר את תוצאת כל בקשה לפי סדר הקלט.
    """
    results = [None] * len(amounts)

    def worker(index: int, amount: float):
        results[index] = manager.attempt_reservation(amount)

    threads = [threading.Thread(target=worker, args=(i, amount)) for i, amount in enumerate(amounts)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results
