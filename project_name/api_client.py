import requests
import time
import logging
<<<<<<< HEAD
import time
from .config import YAHOO_FINANCE_BASE_URL, API_TIMEOUT
=======

from project_trade_order_manager.config import MASSIVE_API_URL, API_TIMEOUT, MAX_RETRIES
>>>>>>> c5e1766c90b4fd0d6e1f895aeb9a39c466ab404d

logger = logging.getLogger(__name__)

def fetch_stock_price(symbol: str) -> dict:
    """
<<<<<<< HEAD
    מבצע קריאת GET ל-API החיצוני כדי למשוך את שער המניה.
    כולל מנגנון Retry של 3 ניסיונות בסך הכול עבור שגיאות תקשורת.
    """
    url = f"{YAHOO_FINANCE_BASE_URL}/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    max_attempts = 3
    
    for attempt in range(1, max_attempts + 1):
        try:
            # שליחת בקשה עם ה-Timeout שהוגדר בקונפיגורציה
            response = requests.get(url, headers=headers, timeout=API_TIMEOUT)
            
            # בדיקת קוד התגובה - יזרוק HTTPError על שגיאות כמו 404 או 500
            response.raise_for_status()
            
            data = response.json()
            
            # שליפת המחיר (יזרוק KeyError או TypeError אם המבנה שונה)
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            return float(price)
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning("כשל תקשורת בניסיון %d מתוך %d עבור %s: %s", attempt, max_attempts, symbol, e)
            if attempt == max_attempts:
                logger.error("מוצו כל %d הניסיונות למשוך נתונים עבור המניה %s.", max_attempts, symbol)
                raise  # דיווח על כשל ברור לאחר הניסיון האחרון
            time.sleep(2)  # המתנה בין הניסיונות
            
        except requests.exceptions.HTTPError as e:
            logger.error("שגיאת HTTP עבור %s: %s", symbol, e)
            raise  # עצירה מיידית - אין ניסיון חוזר על שגיאות HTTP
            
        except (ValueError, KeyError, TypeError) as e:
            logger.error("שגיאה בפענוח הנתונים או נתונים חסרים עבור %s: %s", symbol, e)
            raise  # עצירה מיידית - אין ניסיון חוזר על נתונים לא תקינים
=======
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
>>>>>>> c5e1766c90b4fd0d6e1f895aeb9a39c466ab404d
