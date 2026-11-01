import os

# =====================================================================
# הגדרות שירותי נתונים וקישורי API (Base URLs)
# קובץ: project_name/config.py
# =====================================================================

# 1. Yahoo Finance (מומלץ - חינמי ולא דורש מפתח)
YAHOO_FINANCE_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

# 2. Alpha Vantage (דורש מפתח הרשמה חינמי)
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# 3. Exchange Rates API (לשערי חליפין)
EXCHANGE_RATES_BASE_URL = "https://api.exchangeratesapi.io/v1/latest"

# 4. Financial Modeling Prep (FMP)
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# 5. Apify Stock Price API 
APIFY_STOCK_API_URL = "https://apify.com/api/stock-price-api"

# 6. Massive Stock Market API 
MASSIVE_API_URL = "https://massive.com/landing/stock-market-api-python"

# =====================================================================
# הגדרות מערכת נוספות (לפי סעיף 2 בהוראות)
# =====================================================================

# זמן המתנה מקסימלי לתגובת שרת (בשניות)
API_TIMEOUT = 10 

# מספר ניסיונות חוזרים (Retries) במקרה של כשל רשת
MAX_RETRIES = 3

# זמן המתנה בין ניסיונות חוזרים (בשניות)
RETRY_DELAY = 2

# סמל שער הדולר-שקל ב-Yahoo Finance (משמש לבקרת התקציב בשקלים)
USD_ILS_SYMBOL = "ILS=X"

# =====================================================================
# Google Gemini - ניתוח AI וצ'אט בסוף תרחיש ההדגמה
# =====================================================================
# המפתח נטען מקובץ .env המקומי (לא נשמר ב-Git) או ממשתנה סביבה
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # בלי python-dotenv עדיין אפשר להגדיר את המפתח כמשתנה סביבה

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# אפשר להחליף מודל דרך GEMINI_MODEL ב-.env, בלי לשנות קוד
GEMINI_MODEL = os.environ.get("GEMINI_MODEL") or "gemini-3.5-flash-lite"

# זמן המתנה מקסימלי לתשובת Gemini (במילישניות)
GEMINI_TIMEOUT_MS = 60_000
