import pytest

from project_name.context_managers import OrderProcessingContext
from project_name.models import TradeOrder, MarketOrder, StopLossOrder, Portfolio, TradingPlatform
from project_name.processing import (
    process_regular_queue, process_priority_queue, build_order_dictionaries, describe_symbol_counts
)


# ============================================================
#   התנהגויות משלב 1 - מוודאים שנשמרו אחרי השינויים של שלב 2
# ============================================================

@pytest.fixture
def market_order():
    return MarketOrder("M1", "AAPL", "Buy", 10, 100.0)


@pytest.fixture
def stop_loss_order():
    return StopLossOrder("S1", "TSLA", "Sell", 5, 200.0, stop_price=190.0)


# ---------- ולידציה ----------

@pytest.mark.parametrize("bad_quantity", [0, -3, 2.5, "10"])
def test_quantity_must_be_positive_int(bad_quantity):
    with pytest.raises(ValueError):
        MarketOrder("X", "AAPL", "Buy", bad_quantity, 100.0)


@pytest.mark.parametrize("bad_price", [0, -1.5, "100"])
def test_price_must_be_positive_number(bad_price):
    with pytest.raises(ValueError):
        MarketOrder("X", "AAPL", "Buy", 10, bad_price)


def test_trade_order_is_abstract():
    with pytest.raises(TypeError):
        TradeOrder("X", "AAPL", "Buy", 10, 100.0)


# ---------- פולימורפיזם ותורים ----------

def test_stop_loss_comes_before_market_order(market_order, stop_loss_order):
    # פקודת השוק נוצרה קודם, ובכל זאת פקודת החירום דחופה יותר
    assert stop_loss_order < market_order
    assert process_priority_queue([market_order, stop_loss_order]) == [stop_loss_order]


def test_regular_queue_keeps_arrival_order():
    orders = [MarketOrder(f"M{i}", "AAPL", "Buy", 1, 10.0) for i in range(1, 6)]

    processed = process_regular_queue(orders)

    # התור הרגיל מטפל בארבע הפקודות הראשונות לפי סדר ההגעה
    assert [o.order_id for o in processed] == ["M1", "M2", "M3", "M4"]


def test_order_dictionaries_keep_first_duplicate_and_count_by_symbol():
    first = MarketOrder("A", "AAPL", "Buy", 1, 10.0)
    duplicate = MarketOrder("A", "TSLA", "Buy", 1, 10.0)
    other = MarketOrder("B", "AAPL", "Sell", 1, 10.0)

    orders_by_id, symbol_counts = build_order_dictionaries([first, duplicate, other])

    assert orders_by_id["A"].symbol == "AAPL"  # מזהה כפול: נשמרת הפקודה הראשונה
    assert symbol_counts == {"AAPL": 2, "TSLA": 1}
    assert describe_symbol_counts(symbol_counts) == ["AAPL: 2", "TSLA: 1"]


def test_orders_are_equal_by_id_only():
    assert MarketOrder("A", "AAPL", "Buy", 1, 10.0) == MarketOrder("A", "MSFT", "Sell", 9, 99.0)


# ---------- הרכבה: פלטפורמה ותיק ----------

def test_platform_rejects_duplicate_id_and_sums_volume(market_order):
    platform = TradingPlatform()
    platform.add_order(market_order)
    platform.add_order(MarketOrder("M2", "MSFT", "Buy", 2, 50.0))

    with pytest.raises(ValueError):
        platform.add_order(MarketOrder("M1", "TSLA", "Buy", 1, 1.0))

    assert len(platform) == 2
    assert platform.get_total_volume() == 1100.0  # 10*100 + 2*50


def test_platform_and_portfolio_have_readable_representations(market_order):
    platform = TradingPlatform()
    platform.add_order(market_order)

    assert str(platform) == "פלטפורמת מסחר: 1 פקודות, שווי כולל 1000.0"
    assert repr(platform) == "TradingPlatform(orders=['M1'])"
    assert repr(Portfolio(500)) == "Portfolio(balance=500, holdings={})"


def test_portfolio_does_not_reserve_more_than_balance():
    portfolio = Portfolio(1000)

    assert portfolio.reserve_funds(1500) is False
    assert portfolio.balance == 1000
    assert portfolio.reserve_funds(400) is True
    assert portfolio.balance == 600


# ---------- Context Manager ----------

def test_context_manager_restores_status_and_reraises(market_order):
    with pytest.raises(ConnectionError):
        with OrderProcessingContext(market_order):
            raise ConnectionError("down")

    assert market_order.status == "ממתינה"


def test_context_manager_marks_order_done(market_order):
    with OrderProcessingContext(market_order) as order:
        assert order.status == "בטיפול"

    assert market_order.status == "בוצעה"
