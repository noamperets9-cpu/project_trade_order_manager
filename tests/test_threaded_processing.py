import pytest

from project_name.models import Portfolio
from project_name.threaded_processing import SafePortfolioManager, run_concurrent_reservations


# ============================================================
#     בדיקות ל-Threads ו-Lock (סעיף 5.2)
# ============================================================
# בודקים את מספר האישורים ואת היתרה הסופית, ולא איזה Thread קיבל אישור.


@pytest.mark.parametrize("balance, amounts, expected_approved, expected_balance", [
    (5000, [3000, 3000], 1, 2000),        # התרחיש מה-README: רק סוחר אחד מאושר
    (10000, [3000, 3000, 3000], 3, 1000),  # יש מספיק לכולם
    (1000, [100] * 20, 10, 0),             # 20 סוחרים, היתרה מספיקה בדיוק ל-10
])
def test_concurrent_reservations_never_overdraw(balance, amounts, expected_approved, expected_balance):
    portfolio = Portfolio(balance)
    manager = SafePortfolioManager(portfolio)

    results = run_concurrent_reservations(manager, amounts)

    assert results.count(True) == expected_approved
    assert manager.successful_reservations == expected_approved
    assert portfolio.balance == expected_balance
    assert portfolio.balance >= 0


def test_rejected_reservation_does_not_change_balance():
    portfolio = Portfolio(500)
    manager = SafePortfolioManager(portfolio)

    assert manager.attempt_reservation(800) is False
    assert portfolio.balance == 500
    assert manager.successful_reservations == 0
