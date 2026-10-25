import requests
import logging
from .config import YAHOO_FINANCE_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)

def fetch_stock_price(symbol: str) -> float:
    """
    מבצע קריאת GET ל-API החיצוני כדי למשוך את שער המניה.
    אם יש כשל ברשת או פענוח, הקוד פשוט יקרוס.
    """
    url = f"{YAHOO_FINANCE_BASE_URL}/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # שליחת בקשה בודדת ללא Retry (כי אין לנו Try/Except)
    response = requests.get(url, headers=headers, timeout=API_TIMEOUT)
    
    # נוודא שהבקשה עברה לפני שננסה לפענח JSON
    response.raise_for_status()
    
    data = response.json()
    
    # אין הגנה מ-KeyError: אם המבנה שונה, הקוד ייפול.
    price = data['chart']['result'][0]['meta']['regularMarketPrice']
    return float(price)