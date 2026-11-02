import pytest

from project_name.reports import summarize_policy
from project_name.services import ApprovalResult


# ============================================================
#   יכולת שפותחה ב-TDD: סיכום החלטות של מדיניות למנהל הסיכונים
# ============================================================
# הדרישה העסקית: לכל מדיניות מציגים כמה פקודות אושרו, כמה נדחו,
# כמה תקציב שוריין ואיזה אחוז מהתקציב ההתחלתי נוצל.
# התוצאות הצפויות חושבו ידנית מהדרישה.


def test_summary_counts_decisions_and_budget_use():
    results = [
        ApprovalResult("O1", True, 4000.0, "אושרה"),
        ApprovalResult("O2", False, 9000.0, "נדחתה"),
        ApprovalResult("O3", True, 2000.0, "אושרה"),
    ]

    summary = summarize_policy(results, initial_balance=10_000)

    assert summary.approved == 2
    assert summary.rejected == 1
    assert summary.reserved_ils == 6000.0
    assert summary.utilization_pct == 60.0


def test_summary_without_orders_is_empty():
    summary = summarize_policy([], initial_balance=10_000)

    assert (summary.approved, summary.rejected, summary.reserved_ils, summary.utilization_pct) == (0, 0, 0.0, 0.0)


@pytest.mark.parametrize("bad_balance", [0, -500])
def test_summary_requires_positive_initial_balance(bad_balance):
    with pytest.raises(ValueError):
        summarize_policy([], initial_balance=bad_balance)
