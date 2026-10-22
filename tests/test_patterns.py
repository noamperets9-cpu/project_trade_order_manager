import json

import pytest

from factories import OrderFactory
from models import MarketOrder, StopLossOrder, Portfolio
from repository import load_orders_from_file
from services import OrderApprovalService
from strategies import FullBalancePolicy, RiskLimitPolicy


# ============================================================
#     בדיקות לתבניות התכנון של שלב 2 (Factory + Strategy)
# ============================================================

@pytest.fixture
def factory():
    return OrderFactory()


@pytest.fixture
def buy_order_data():
    return {"id": "T1", "symbol": "AAPL", "action": "Buy", "quantity": 10, "price": 100.0}


# ---------- Factory ----------

@pytest.mark.parametrize("data, expected_class, expected_priority", [
    ({"type": "market"}, MarketOrder, 2),
    ({"type": "stop_loss", "stop_price": 95.0}, StopLossOrder, 1),
    ({}, MarketOrder, 2),  # שורה משלב 1 ללא type: נשמרת ההתנהגות הקודמת
])
def test_factory_creates_order_by_type(factory, buy_order_data, data, expected_class, expected_priority):
    order = factory.create({**buy_order_data, **data})
    assert type(order) is expected_class
    assert order.get_priority() == expected_priority


def test_factory_stop_loss_keeps_stop_price(factory, buy_order_data):
    order = factory.create({**buy_order_data, "type": "stop_loss", "stop_price": 95.0})
    assert order.stop_price == 95.0


@pytest.mark.parametrize("bad_data", [
    {"type": "futures"},           # סוג לא מוכר
    {"type": "stop_loss"},         # חסר stop_price
    {"type": "market", "quantity": -5},  # כמות לא חוקית
])
def test_factory_rejects_invalid_input(factory, buy_order_data, bad_data):
    with pytest.raises(ValueError):
        factory.create({**buy_order_data, **bad_data})


def test_repository_uses_factory_for_mixed_file(tmp_path):
    rows = [
        {"id": "A", "symbol": "AAPL", "action": "Buy", "quantity": 1, "price": 10, "type": "market"},
        {"id": "B", "symbol": "TSLA", "action": "Sell", "quantity": 1, "price": 10,
         "type": "stop_loss", "stop_price": 9},
        {"id": "C", "symbol": "X", "action": "Buy", "quantity": 1, "price": 10, "type": "unknown"},
    ]
    path = tmp_path / "orders.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    orders = list(load_orders_from_file(str(path)))

    # השורה עם הסוג הלא מוכר מדולגת, השתיים האחרות נוצרות מהסוג הנכון
    assert [type(o) for o in orders] == [MarketOrder, StopLossOrder]


# ---------- Strategy ----------

@pytest.mark.parametrize("policy, cost, balance, expected", [
    (FullBalancePolicy(), 900, 1000, True),
    (FullBalancePolicy(), 1000, 1000, True),    # גבול: בדיוק כל היתרה
    (FullBalancePolicy(), 1001, 1000, False),
    (RiskLimitPolicy(0.25), 250, 1000, True),   # גבול: בדיוק 25%
    (RiskLimitPolicy(0.25), 251, 1000, False),
])
def test_policies_decide_by_their_own_rule(policy, cost, balance, expected):
    assert policy.can_approve(cost, balance) is expected


@pytest.mark.parametrize("bad_share", [0, -0.1, 1.5])
def test_risk_limit_rejects_invalid_share(bad_share):
    with pytest.raises(ValueError):
        RiskLimitPolicy(bad_share)


# ---------- Service (Strategy מוזרקת מבחוץ) ----------

def make_order(order_id, action="Buy", quantity=10, price=100.0):
    return MarketOrder(order_id, "AAPL", action, quantity, price)


def test_service_reserves_budget_in_ils():
    # 10 מניות * 100$ * שער 4 = 4,000 ש"ח
    portfolio = Portfolio(10_000)
    service = OrderApprovalService(portfolio, FullBalancePolicy(), rate_provider=lambda: 4.0)

    [result] = service.review_orders([make_order("O1")])

    assert result.approved is True
    assert result.cost_ils == 4000.0
    assert portfolio.balance == 6000.0


def test_same_orders_different_policy_give_different_decision():
    orders = [make_order("O1")]  # עלות 4,000 ש"ח מתוך יתרה של 10,000 (40%)

    full = OrderApprovalService(Portfolio(10_000), FullBalancePolicy(), lambda: 4.0)
    strict = OrderApprovalService(Portfolio(10_000), RiskLimitPolicy(0.25), lambda: 4.0)

    assert full.review_orders(orders)[0].approved is True
    assert strict.review_orders(orders)[0].approved is False


def test_service_stops_approving_when_budget_runs_out():
    portfolio = Portfolio(5_000)
    service = OrderApprovalService(portfolio, FullBalancePolicy(), lambda: 4.0)

    results = service.review_orders([make_order("O1"), make_order("O2")])

    assert [r.approved for r in results] == [True, False]
    assert portfolio.balance == 1000.0


def test_sell_orders_do_not_use_budget():
    portfolio = Portfolio(1_000)
    service = OrderApprovalService(portfolio, FullBalancePolicy(), lambda: 4.0)

    [result] = service.review_orders([make_order("S1", action="Sell")])

    assert result.approved is True
    assert portfolio.balance == 1000


@pytest.mark.parametrize("rate_provider", [
    lambda: (_ for _ in ()).throw(ConnectionError("down")),  # השירות לא זמין
    lambda: -3.7,                                            # שער לא תקין
])
def test_no_approval_and_no_reservation_without_valid_rate(rate_provider):
    portfolio = Portfolio(10_000)
    service = OrderApprovalService(portfolio, FullBalancePolicy(), rate_provider)

    [result] = service.review_orders([make_order("O1")])

    assert result.approved is False
    assert portfolio.balance == 10_000  # לא בוצע עדכון עסקי שגוי
