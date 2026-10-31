import pytest
import requests
from unittest.mock import patch
from project_name.api_client import fetch_stock_price

# נגדיר Mock לפונקציה requests.get לאורך כל הבדיקות בקובץ הזה
@patch('project_name.api_client.requests.get')
def test_fetch_stock_price_success(mock_get):
    """בדיקת הצלחה: פענוח JSON תקין מתוך מבנה תקין"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'chart': {'result': [{'meta': {'regularMarketPrice': 150.5}}]}
    }
    
    price = fetch_stock_price("AAPL")
    
    assert price == 150.5
    # מוודא שבוצעה קריאה אחת בלבד
    assert mock_get.call_count == 1

@patch('project_name.api_client.requests.get')
def test_fetch_stock_price_retry_and_timeout(mock_get):
    """בדיקת כשל זמני: ה-API נופל, המערכת מנסה 3 פעמים ורק אז זורקת Timeout"""
    # הגדרת ה-Mock כך שיזרוק שגיאת Timeout בכל קריאה
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
    
    # הבדיקה תוודא שהפונקציה אכן זורקת את השגיאה בסוף
    with pytest.raises(requests.exceptions.Timeout):
        # כדי לא לעכב את הבדיקות האוטומטיות נדרוס זמנית את ה-time.sleep
        with patch('project_name.api_client.time.sleep'):
            fetch_stock_price("AAPL")
    
    # מוודא שהפונקציה ניסתה לגשת לרשת בדיוק 3 פעמים (מנגנון ה-Retry)
    assert mock_get.call_count == 3

@patch('project_name.api_client.requests.get')
def test_fetch_stock_price_http_error(mock_get):
    """בדיקת שגיאת HTTP (כמו 404): הפונקציה צריכה לקרוס מיד ללא Retry"""
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    
    with pytest.raises(requests.exceptions.HTTPError):
        fetch_stock_price("INVALID_SYMBOL")
        
    # מוודא שהפונקציה הפסיקה מיד אחרי הניסיון הראשון ולא עשתה Retry
    assert mock_get.call_count == 1

@patch('project_name.api_client.requests.get')
def test_fetch_stock_price_missing_field(mock_get):
    """בדיקת JSON חסר/פגום: הפונקציה זורקת KeyError ולא מנסה שוב"""
    mock_get.return_value.status_code = 200
    # נחזיר JSON שחסר בו המפתח 'meta'
    mock_get.return_value.json.return_value = {
        'chart': {'result': [{'wrong_key': 150.5}]}
    }
    
    with pytest.raises(KeyError):
        fetch_stock_price("AAPL")
        
    assert mock_get.call_count == 1