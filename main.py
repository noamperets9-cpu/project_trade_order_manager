import asyncio
from bidi.algorithm import get_display
from project_name.models import Portfolio, MarketOrder
from project_name.services import OrderApprovalService
from project_name.strategies import ApprovalPolicy
from project_name.api_client import fetch_stock_price
from project_name.async_processing import collect_statuses_concurrently

class BasicPolicy(ApprovalPolicy):
    def can_approve(self, cost_ils: float, balance: float) -> bool:
        return cost_ils <= balance
    @property
    def name(self) -> str:
        return "Basic Policy"

def main():
    print(get_display("=== הדגמת מערכת ניהול המסחר ==="))
    
    print(get_display("\n1. מושך שער מניית AAPL מ-Yahoo Finance..."))
    try:
        price = fetch_stock_price("AAPL")
        print(get_display(f"שער המניה הנוכחי נמשך בהצלחה: {price}$"))
    except Exception as e:
        print(get_display(f"שגיאה במשיכת נתונים מהרשת: {e}"))
        price = 150.0  

    print(get_display("\n2. בודק פקודת קנייה מול בקרת התקציב..."))
    portfolio = Portfolio(initial_balance=5000.0)
    order = MarketOrder("O1", "AAPL", "buy", 10, price)
    
    service = OrderApprovalService(portfolio, BasicPolicy(), rate_provider=lambda: 3.7)
    
    results = service.review_orders([order])
    for res in results:
        msg = f"סטטוס פקודה {res.order_id}: אושר={res.approved}, עלות={res.cost_ils} ש\"ח. סיבה: {res.reason}"
        print(get_display(msg))
    
    print(get_display(f"יתרה פנויה נותרת בתיק: {portfolio.balance} ש\"ח"))

    print(get_display("\n3. אוסף סטטוס של 3 פקודות במקביל (Async)..."))
    order_ids = ["O1", "O2", "O3"]
    async_results = asyncio.run(collect_statuses_concurrently(order_ids))
    print(get_display(f"תוצאות אסינכרוניות שהתקבלו: {async_results}"))
    
    print(get_display("\n=== סיום הדגמה ==="))

if __name__ == "__main__":
    main()