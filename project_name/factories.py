from models import TradeOrder, MarketOrder, StopLossOrder

# ============================================================
#           שלב 2, סעיף 3 - תבנית Factory ליצירת פקודות
# ============================================================
# הצורך: בשלב 1 כל שורה בקובץ הנתונים הפכה תמיד ל-MarketOrder,
# ולכן פקודות חירום (Stop-Loss) לא הגיעו לתור העדיפויות.
# ה-Factory מרכז במקום אחד את ההחלטה איזה סוג פקודה ליצור לפי השדה "type",
# כך ששאר הקוד (repository, services) לא צריך לדעת אילו מחלקות קיימות.

MARKET = "market"
STOP_LOSS = "stop_loss"


class OrderFactory:
    """ יוצר אובייקט פקודה מהסוג המתאים מתוך מילון נתונים """

    def create(self, data: dict) -> TradeOrder:
        """ בוחר את מחלקת הפקודה לפי השדה type ומחזיר מופע מוכן """
        if not isinstance(data, dict):
            raise ValueError("נתוני הפקודה חייבים להיות מילון")

        # שורות משלב 1 ללא שדה type נחשבות לפקודות שוק רגילות
        order_type = str(data.get("type", MARKET)).lower()

        try:
            if order_type == MARKET:
                return MarketOrder(
                    order_id=data["id"],
                    symbol=data["symbol"],
                    action=data["action"],
                    quantity=data["quantity"],
                    price=data["price"],
                )
            elif order_type == STOP_LOSS:
                return StopLossOrder(
                    order_id=data["id"],
                    symbol=data["symbol"],
                    action=data["action"],
                    quantity=data["quantity"],
                    price=data["price"],
                    stop_price=data["stop_price"],
                )
        except KeyError as error:
            raise ValueError(f"חסר שדה חובה ליצירת פקודה: {error}") from error

        raise ValueError(f"סוג פקודה לא מוכר: {order_type}")
