import threading
import time
from .models import Portfolio

class SafePortfolioManager:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self._lock = threading.Lock()
        self.successful_reservations = 0

    def attempt_reservation(self, amount: float):
        """
        ניסיון שריון מהקופה המשותפת תוך הגנה עם Lock.
        ללא ה-Lock, עלולה לקרות שגיאה שבה Thread A ו-Thread B 
        קוראים יחד את היתרה לפני שהיא מתעדכנת.
        """
        with self._lock:
            if self.portfolio.balance >= amount:
                time.sleep(0.01) # סימולציה לעיבוד כדי להבליט את הצורך בנעילה
                self.portfolio.reserve_funds(amount)
                self.successful_reservations += 1