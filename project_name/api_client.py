import requests
import time
import logging
from requests.exceptions import Timeout, ConnectionError, HTTPError

# ייבוא ההגדרות שיצרנו בקובץ config.py
from project_trade_order_manager.config import MASSIVE_API_URL, API_TIMEOUT, MAX_RETRIES

logger = logging.getLogger(__name__)

def fetch_stock_price(symbol: str) -> dict:
    """
    מושך נתוני מניה משירות חיצוני.
    מבצע עד 3 ניסיונות במקרה של כשל תקשורת, אך זורק שגיאה מידית במקרים של נתונים פגומים.
    """
    # החלף את נתיב ה-URL הספציפי בהתאם למבנה של ה-API שבחרת
    url = f"{MASSIVE_API_URL}/quote/{symbol}" 
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # שימוש ב-timeout מתוך קובץ ההגדרות
            response = requests.get(url, timeout=API_TIMEOUT)
            
            # בדיקת קוד התגובה (זורק חריגה עבור שגיאות 4xx ו-5xx)
            response.raise_for_status()
            
            # פענוח ה-JSON
            data = response.json()
            
            # בדיקת השדות הדרושים
            if not data or "price" not in data:
                raise KeyError(f"Missing required 'price' field for {symbol}")
                
            return data
            
        except (ConnectionError, Timeout) as e:
            logger.warning(f"Network error on attempt {attempt}/{MAX_RETRIES} for {symbol}: {e}")
            if attempt == MAX_RETRIES:
                logger.error(f"Failed to fetch data for {symbol} after {MAX_RETRIES} attempts.")
                raise  # מיצוי ניסיונות - זורק את השגיאה הלאה
            
            time.sleep(2)  # המתנה קצרה לפני ניסיון חוזר
            
        except HTTPError as e:
            logger.error(f"HTTP Error for {symbol}: {e}")
            raise  # שגיאת שרת או בקשה לא תקינה - לא מנסים שוב אוטומטית