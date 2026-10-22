from abc import ABC, abstractmethod

# ============================================================
#        שלב 2, סעיף 3 - תבנית Strategy למדיניות אישור תקציב
# ============================================================
# הצורך: מנהל הסיכונים (CFO) קובע את מדיניות האישור של פקודות קנייה.
# יש יותר מדרך אחת להחליט אם פקודה מאושרת, וכל המדיניות חולקות חוזה אחד.
# שירות האישור מקבל את המדיניות מבחוץ, כך שאפשר להחליף מדיניות
# בלי לשנות את קוד השירות, ולבדוק כל מדיניות בנפרד.


class ApprovalPolicy(ABC):
    """ חוזה משותף: האם אפשר לאשר פקודה בעלות נתונה מול היתרה הפנויה """

    name = "מדיניות בסיס"

    @abstractmethod
    def can_approve(self, cost_ils: float, available_balance: float) -> bool:
        """ מחזיר True אם הפקודה מאושרת לפי המדיניות """


class FullBalancePolicy(ApprovalPolicy):
    """ מדיניות מקלה: מאשרת כל פקודה שהיתרה הפנויה מכסה """

    name = "ניצול מלא של היתרה"

    def can_approve(self, cost_ils: float, available_balance: float) -> bool:
        return 0 < cost_ils <= available_balance


class RiskLimitPolicy(ApprovalPolicy):
    """ מדיניות שמרנית: פקודה בודדת לא תנצל יותר מאחוז מסוים מהיתרה הפנויה """

    def __init__(self, max_share: float = 0.25):
        if not 0 < max_share <= 1:
            raise ValueError("אחוז החשיפה המרבי חייב להיות בין 0 ל-1")
        self.max_share = max_share
        self.name = f"הגבלת חשיפה ({max_share:.0%} מהיתרה לפקודה)"

    def can_approve(self, cost_ils: float, available_balance: float) -> bool:
        return 0 < cost_ils <= available_balance * self.max_share
