import logging
import time

import requests

from .config import YAHOO_FINANCE_BASE_URL, API_TIMEOUT, MAX_RETRIES, RETRY_DELAY, USD_ILS_SYMBOL

logger = logging.getLogger(__name__)

# ============================================================
#   שלב 2, סעיף 2 - חיבור לשירות חיצוני (Yahoo Finance)
# ============================================================
# המודול אחראי רק על התקשורת ובדיקת התגובה.
# ההחלטה העסקית מה לעשות עם המידע נמצאת ב-services.py.
#
# סוגי הכשל שמובחנים כאן:
#   - כשל תקשורת (Timeout / ConnectionError) -> עד MAX_RETRIES ניסיונות, עם המתנה ביניהם
#   - שגיאת HTTP (404, 500 וכו')              -> נזרק מיד, ללא ניסיון חוזר
#   - JSON שאינו ניתן לפענוח                  -> נזרק מיד (ValueError)
#   - נתונים שאינם תואמים למבנה / ערך לא חוקי -> נזרק מיד (KeyError / ValueError)


def fetch_stock_price(symbol: str) -> float:
    """
    מבצע קריאת GET ל-Yahoo Finance ומחזיר את המחיר הנוכחי של הסמל.
    כולל Retry של עד MAX_RETRIES ניסיונות בסך הכול, רק עבור שגיאות תקשורת.
    """
    url = f"{YAHOO_FINANCE_BASE_URL}/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"interval": "1d", "range": "1d"}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # שליחת בקשה עם ה-Timeout שהוגדר בקונפיגורציה
            response = requests.get(url, headers=headers, params=params, timeout=API_TIMEOUT)

            # בדיקת קוד התגובה - יזרוק HTTPError על שגיאות כמו 404 או 500
            response.raise_for_status()

            data = response.json()

            # שליפת המחיר ובדיקת תקינותו (KeyError אם המבנה שונה)
            try:
                price = float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])
            except (IndexError, TypeError) as error:
                raise KeyError(f"מבנה תשובה לא צפוי עבור {symbol}") from error

            if price <= 0:
                raise ValueError(f"מחיר לא חוקי עבור {symbol}: {price}")

            logger.info("נמשך מחיר עבור %s: %s", symbol, price)
            return price

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning("כשל תקשורת בניסיון %d מתוך %d עבור %s: %s", attempt, MAX_RETRIES, symbol, e)
            if attempt == MAX_RETRIES:
                logger.error("מוצו כל %d הניסיונות למשוך נתונים עבור %s.", MAX_RETRIES, symbol)
                raise  # דיווח על כשל ברור לאחר הניסיון האחרון
            time.sleep(RETRY_DELAY)  # המתנה בין הניסיונות

        except requests.exceptions.HTTPError as e:
            logger.error("שגיאת HTTP עבור %s: %s", symbol, e)
            raise  # עצירה מיידית - אין ניסיון חוזר על שגיאות HTTP

        except (ValueError, KeyError) as e:
            logger.error("שגיאה בפענוח הנתונים או נתונים חסרים עבור %s: %s", symbol, e)
            raise  # עצירה מיידית - אין ניסיון חוזר על נתונים לא תקינים


def fetch_usd_ils_rate() -> float:
    """ מחזיר את שער הדולר-שקל העדכני (משמש כמקור השער של OrderApprovalService) """
    return fetch_stock_price(USD_ILS_SYMBOL)
