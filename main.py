import json
import requests
import os

# =====================================================================
# TradeInsight Command - הגדרת כתובות שירותי נתונים (Global Variables)
# =====================================================================

# 1. Financial Modeling Prep
FMP_DOCS_URL = "https://site.financialmodelingprep.com/developer/docs"
FMP_API_BASE_URL = "https://financialmodelingprep.com/api/v3"

# 2. Exchange Rates API
EXCHANGE_RATES_URL = "https://exchangeratesapi.io/"

# 3. Alpha Vantage
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/"

# 4. Yahoo Finance
YAHOO_FINANCE_URL = "https://finance.yahoo.com/"

# 5. Apify Stock Price API
APIFY_STOCK_API_URL = "https://apify.com/api/stock-price-api"

# 6. Massive Stock Market API
MASSIVE_API_URL = "https://massive.com/landing/stock-market-api-python"


# =====================================================================
# לוגיקת הפרויקט המקומית - שלב א'
# =====================================================================

class Open_files:
    def __init__(self, file_name):
        self.file_name = file_name

    def open_file(self):
        # פתיחת הקובץ וטעינת נתוני ה-JSON לזיכרון
        with open(self.file_name, 'r', encoding='utf-8') as json_file:
            workouts = json.load(json_file)  # הופך ישירות ל-list של מילונים

