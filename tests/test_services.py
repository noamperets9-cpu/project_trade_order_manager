import json
from unittest.mock import Mock, patch

import pytest
import requests

from project_name.api_client import fetch_usd_ils_rate
from project_name.models import Portfolio, StopLossOrder
from project_name.repository import load_orders_from_file
from project_name.services import OrderApprovalService
from project_name.strategies import FullBalancePolicy


# ============================================================
#   תהליך משולב: קובץ -> Factory -> שער מהשירות -> Strategy -> תיק
# ============================================================
# רק התלות החיצונית מוחלפת (requests.get ו-time.sleep). קריאת הקובץ,
# ה-Factory, ה-api_client, השירות והמדיניות רצים כמו בהרצה האמיתית.

ROWS = [
    {"id": "A1", "symbol": "AAPL", "action": "Buy", "quantity": 10, "price": 100.0, "type": "market"},
    {"id": "A2", "symbol": "MSFT", "action": "Buy", "quantity": 20, "price": 50.0, "type": "market"},
    {"id": "A3", "symbol": "TSLA", "action": "Sell", "quantity": 5, "price": 200.0,
     "type": "stop_loss", "stop_price": 180.0},
    {"id": "A4", "symbol": "NVDA", "action": "Buy", "quantity": 30, "price": 100.0, "type": "market"},
]


@pytest.fixture
def orders_file(tmp_path):
    path = tmp_path / "orders.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in ROWS), encoding="utf-8")
    return str(path)


@pytest.fixture(autouse=True)
def no_real_sleep():
    with patch("project_name.api_client.time.sleep"):
        yield


def yahoo_response(rate):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"chart": {"result": [{"meta": {"regularMarketPrice": rate}}]}}
    return response


@patch("project_name.api_client.requests.get")
def test_full_flow_from_file_to_budget(mock_get, orders_file):
    mock_get.return_value = yahoo_response(4.0)
    orders = list(load_orders_from_file(orders_file))
    portfolio = Portfolio(15_000)
    service = OrderApprovalService(portfolio, FullBalancePolicy(), rate_provider=fetch_usd_ils_rate)

    results = service.review_orders(orders)

    # A1: 10*100*4 = 4,000 | A2: 20*50*4 = 4,000 | A3: מכירה | A4: 30*100*4 = 12,000 > 7,000 שנותרו
    assert isinstance(orders[2], StopLossOrder)
    assert [(r.order_id, r.approved) for r in results] == [
        ("A1", True), ("A2", True), ("A3", True), ("A4", False)]
    assert portfolio.balance == 7_000


@patch("project_name.api_client.requests.get")
def test_full_flow_when_service_is_down(mock_get, orders_file):
    mock_get.side_effect = requests.exceptions.Timeout("timeout")
    portfolio = Portfolio(15_000)
    service = OrderApprovalService(portfolio, FullBalancePolicy(), rate_provider=fetch_usd_ils_rate)

    results = service.review_orders(load_orders_from_file(orders_file))

    assert mock_get.call_count == 3              # מוצו כל הניסיונות
    assert not any(r.approved for r in results)  # אף פקודה לא אושרה
    assert portfolio.balance == 15_000           # והתקציב לא השתנה
