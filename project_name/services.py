import logging
from dataclasses import dataclass
from typing import Callable, Iterable

from models import TradeOrder, Portfolio
from strategies import ApprovalPolicy

logger = logging.getLogger(__name__)

# ============================================================
#     שלב 2 - שירות עסקי: בקרת תקציב בשקלים לפקודות קנייה
# ============================================================
# השירות מחבר את הרכיבים (תיק, מדיניות אישור, מקור שער) בלי ליצור אותם בעצמו.
# כל התלויות מועברות דרך הבנאי (Dependency Injection):
#   - portfolio      : התיק שממנו משוריין התקציב
#   - policy         : Strategy שמחליטה אם לאשר (strategies.py)
#   - rate_provider  : פונקציה שמחזירה שער USD->ILS. בהרצה רגילה זה שער מדומה,
#                      ובהרצה מול הרשת זו פונקציה מ-api_client.py (סעיף 2).
# כך אפשר להחליף מדיניות או מקור שער, ובבדיקות להעביר שער קבוע בלי רשת.


@dataclass(frozen=True)
class ApprovalResult:
    """ תוצאת בדיקת התקציב של פקודה אחת """
    order_id: str
    approved: bool
    cost_ils: float
    reason: str


class OrderApprovalService:
    def __init__(self, portfolio: Portfolio, policy: ApprovalPolicy,
                 rate_provider: Callable[[], float]):
        self.portfolio = portfolio
        self.policy = policy
        self.rate_provider = rate_provider

    def review_orders(self, orders: Iterable[TradeOrder]) -> list:
        """ ממיר כל פקודת קנייה לשקלים, מחליט לפי המדיניות ומשריין תקציב """
        orders = list(orders)

        try:
            rate = self.rate_provider()
            if not isinstance(rate, (int, float)) or rate <= 0:
                raise ValueError(f"שער לא תקין: {rate}")
        except Exception as error:
            # אין שער אמין, ולכן אין אישור: כל הפקודות נשארות ממתינות
            logger.error("בקרת התקציב לא בוצעה, אין שער זמין: %s", error)
            return [ApprovalResult(o.order_id, False, 0.0, "אין שער זמין, הפקודה ממתינה")
                    for o in orders]

        logger.info("בקרת תקציב לפי שער %.4f ומדיניות '%s'", rate, self.policy.name)
        return [self._review_single(order, rate) for order in orders]

    def _review_single(self, order: TradeOrder, rate: float) -> ApprovalResult:
        """ מחליט על פקודה אחת """
        if order.action.lower() != "buy":
            return ApprovalResult(order.order_id, True, 0.0, "מכירה, לא נדרש תקציב")

        cost_ils = round(order.quantity * order.price * rate, 2)

        if not self.policy.can_approve(cost_ils, self.portfolio.balance):
            logger.info("פקודה %s נדחתה (עלות %.2f ש\"ח)", order.order_id, cost_ils)
            return ApprovalResult(order.order_id, False, cost_ils, "נדחתה לפי מדיניות התקציב")

        if not self.portfolio.reserve_funds(cost_ils):
            return ApprovalResult(order.order_id, False, cost_ils, "אין מספיק יתרה")

        logger.info("פקודה %s אושרה, שוריינו %.2f ש\"ח", order.order_id, cost_ils)
        return ApprovalResult(order.order_id, True, cost_ils, "אושרה ושוריין תקציב")
