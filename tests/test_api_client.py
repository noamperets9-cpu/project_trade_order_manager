import pytest
import requests
from unittest.mock import patch, Mock

from project_name.api_client import fetch_stock_price, fetch_usd_ils_rate

# ============================================================
#   בדיקות לחיבור לשירות החיצוני - ללא רשת וללא המתנות אמיתיות
# ============================================================
# requests.get מוחלף ב-Mock, ו-time.sleep מוחלף כדי שה-Retry לא ימתין באמת.


def yahoo_response(price):
    """ תשובה מדומה במבנה של Yahoo Finance """
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"chart": {"result": [{"meta": {"regularMarketPrice": price}}]}}
    return response


@pytest.fixture(autouse=True)
def no_real_sleep():
    with patch("project_name.api_client.time.sleep") as mock_sleep:
        yield mock_sleep


@patch("project_name.api_client.requests.get")
def test_fetch_stock_price_success(mock_get):
    """ הצלחה: פענוח JSON תקין והחזרת המחיר """
    mock_get.return_value = yahoo_response(150.5)

    assert fetch_stock_price("AAPL") == 150.5
    assert mock_get.call_count == 1


@patch("project_name.api_client.requests.get")
def test_fetch_stock_price_retry_and_timeout(mock_get, no_real_sleep):
    """ Timeout קבוע: 3 ניסיונות בסך הכול, ואז דיווח על הכשל """
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

    with pytest.raises(requests.exceptions.Timeout):
        fetch_stock_price("AAPL")

    assert mock_get.call_count == 3
    assert no_real_sleep.call_count == 2  # המתנה בין הניסיונות, לא אחרי האחרון


@patch("project_name.api_client.requests.get")
def test_fetch_stock_price_retry_success_after_failure(mock_get):
    """ כשל זמני: הניסיון הראשון נכשל, השני מצליח """
    mock_get.side_effect = [requests.exceptions.ConnectionError("Temporary network drop"),
                            yahoo_response(160.0)]

    assert fetch_stock_price("AAPL") == 160.0
    assert mock_get.call_count == 2


@patch("project_name.api_client.requests.get")
def test_fetch_stock_price_http_error(mock_get):
    """ שגיאת HTTP (404): עצירה מיידית ללא Retry """
    response = Mock()
    response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_get.return_value = response

    with pytest.raises(requests.exceptions.HTTPError):
        fetch_stock_price("INVALID_SYMBOL")

    assert mock_get.call_count == 1


@pytest.mark.parametrize("bad_json", [
    {"chart": {"result": [{"wrong_key": 150.5}]}},   # חסר meta
    {"chart": {"result": []}},                       # רשימת תוצאות ריקה
    {"chart": {"result": None}},                     # תוצאה ריקה
])
@patch("project_name.api_client.requests.get")
def test_fetch_stock_price_missing_field(mock_get, bad_json):
    """ שדה נדרש חסר: KeyError ללא ניסיון חוזר """
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = bad_json
    mock_get.return_value = response

    with pytest.raises(KeyError):
        fetch_stock_price("AAPL")

    assert mock_get.call_count == 1


@patch("project_name.api_client.requests.get")
def test_fetch_stock_price_invalid_price(mock_get):
    """ מחיר לא חוקי (אפס או שלילי): הנתונים נדחים """
    mock_get.return_value = yahoo_response(-3.7)

    with pytest.raises(ValueError):
        fetch_stock_price("AAPL")


@patch("project_name.api_client.requests.get")
def test_fetch_stock_price_broken_json(mock_get):
    """ JSON שאינו ניתן לפענוח: נזרק מיד, ללא ניסיון חוזר """
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError("Expecting value")
    mock_get.return_value = response

    with pytest.raises(ValueError):
        fetch_stock_price("AAPL")

    assert mock_get.call_count == 1


@patch("project_name.api_client.requests.get")
def test_fetch_usd_ils_rate_uses_currency_symbol(mock_get):
    """ שער הדולר-שקל נמשך מאותו שירות, עם הסמל ILS=X """
    mock_get.return_value = yahoo_response(3.7)

    assert fetch_usd_ils_rate() == 3.7
    assert mock_get.call_args.args[0].endswith("/ILS=X")
