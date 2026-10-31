import requests
import logging
import time
from .config import YAHOO_FINANCE_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)

def fetch_stock_price(symbol: str) -> float:
    """
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