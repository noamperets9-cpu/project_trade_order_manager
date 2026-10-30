import pytest
from unittest.mock import patch, Mock
from requests.exceptions import Timeout, HTTPError, ConnectionError

# יש לוודא ששם פונקציית הקריאה תואם למה שהגדרת ב- api_client.py
from project_trade_order_manager.api_client import fetch_stock_price

# 1. בדיקת תרחיש הצלחה רגיל
@patch('project_trade_order_manager.api_client.requests.get')
def test_fetch_stock_price_success(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    # מבנה JSON מדומה של מחיר מניה תקין
    mock_response.json.return_value = {"price": 150.5, "symbol": "AAPL"}
    mock_get.return_value = mock_response

    price = fetch_stock_price("AAPL")
    
    assert price == 150.5
    assert mock_get.call_count == 1

# 2. בדיקת שגיאת HTTP קבועה - מוודאים שאין ניסיונות חוזרים מיותרים
@patch('project_trade_order_manager.api_client.requests.get')
def test_fetch_stock_price_http_error(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    with pytest.raises(HTTPError):
        fetch_stock_price("INVALID_SYMBOL")
        
    # שגיאות הרשאה או 404 לא אמורות לנסות שוב
    assert mock_get.call_count == 1

# 3. בדיקת כשל שרת מוחלט - מיצוי 3 ניסיונות ה- Retry לאחר Timeout
@patch('project_trade_order_manager.api_client.requests.get')
def test_fetch_stock_price_timeout_max_retries(mock_get):
    mock_get.side_effect = Timeout("Server is taking too long")

    with pytest.raises(Timeout):
        fetch_stock_price("AAPL")
        
    # המערכת אמורה לנסות בדיוק 3 פעמים ואז לוותר
    assert mock_get.call_count == 3

# 4. בדיקת התאוששות שרת - הצלחה לאחר כשל זמני (Retry מופעל בהצלחה)
@patch('project_trade_order_manager.api_client.requests.get')
def test_fetch_stock_price_retry_success_after_failure(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"price": 160.0, "symbol": "AAPL"}

    # הניסיון הראשון מחזיר שגיאת רשת, הניסיון השני מצליח
    mock_get.side_effect = [ConnectionError("Temporary network drop"), mock_response]

    price = fetch_stock_price("AAPL")
    
    assert price == 160.0
    assert mock_get.call_count == 2

# 5. בדיקת קלט פגום - נתונים שאינם תואמים למבנה הנדרש
@patch('project_trade_order_manager.api_client.requests.get')
def test_fetch_stock_price_missing_required_field(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    # הפונקציה מצפה לשדה 'price' שלא קיים כאן
    mock_response.json.return_value = {"symbol": "AAPL", "unexpected_field": 100}
    mock_get.return_value = mock_response

    with pytest.raises(KeyError):
        fetch_stock_price("AAPL")
        
    # נתונים פגומים לא גורמים לניסיון חוזר אוטומטי
    assert mock_get.call_count == 1