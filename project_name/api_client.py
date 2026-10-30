import requests
import time
import logging

from project_trade_order_manager.config import MASSIVE_API_URL, API_TIMEOUT, MAX_RETRIES

logger = logging.getLogger(__name__)

def fetch_stock_price(symbol: str) -> dict:
    """
    מושך נתוני מניה משירות חיצוני.
    מיישם מנגנון Retry מינורי עבור שגיאות רשת בלבד (Timeout/ConnectionError).
    שאר השגיאות (HTTP, נתונים חסרים) נזרקות ישירות (Fail Fast).
    """
    url = f"{MASSIVE_API_URL}/quote/{symbol}" 
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # 1. שליחת הבקשה עם Timeout
            response = requests.get(url, timeout=API_TIMEOUT)
            
            # 2. בדיקת HTTP - נזרק מיד אם אין הצלחה (מנגנון מובנה)
            response.raise_for_status()
            
            # 3. פענוח JSON ובדיקת קיום נתונים (יזרוק KeyError / DecodeError טבעי)
            data = response.json()
            if not data or "price" not in data:
                raise KeyError(f"Missing required 'price' field for {symbol}")
                
            return data
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.warning(f"Network error on attempt {attempt}/{MAX_RETRIES} for {symbol}: {e}")
            if attempt == MAX_RETRIES:
                logger.error(f"Failed to fetch data for {symbol} after {MAX_RETRIES} attempts.")
                raise  # מיצוי ניסיונות - זורק את השגיאה
            
            time.sleep(2)  # המתנה קצרה לפני הניסיון הבא