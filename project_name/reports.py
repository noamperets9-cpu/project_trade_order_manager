from dataclasses import dataclass
from typing import Iterable

from .services import ApprovalResult

# ============================================================
#        שלב 2 - דוח למנהל הסיכונים: סיכום החלטות לפי מדיניות
# ============================================================
# היכולת פותחה ב-TDD (tests/test_reports.py).
# הדוח עוזר למנהל הסיכונים להשוות מדיניות: כמה פקודות כל מדיניות מאשרת,
# וכמה מהתקציב היא מנצלת.


@dataclass(frozen=True)
class PolicySummary:
    """ סיכום ההחלטות של מדיניות אחת """
    approved: int
    rejected: int
    reserved_ils: float
    utilization_pct: float


def summarize_policy(results: Iterable[ApprovalResult], initial_balance: float) -> PolicySummary:
    """ סופר אישורים ודחיות, ומחשב כמה תקציב שוריין ואיזה אחוז מהתקציב ההתחלתי נוצל """
    if initial_balance <= 0:
        raise ValueError("התקציב ההתחלתי חייב להיות חיובי")

    results = list(results)
    approved = [r for r in results if r.approved]
    reserved_ils = round(sum(r.cost_ils for r in approved), 2)

    return PolicySummary(
        approved=len(approved),
        rejected=len(results) - len(approved),
        reserved_ils=reserved_ils,
        utilization_pct=round(reserved_ils / initial_balance * 100, 1),
    )
