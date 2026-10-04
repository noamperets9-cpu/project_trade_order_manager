import json
from models import MarketOrder

# ============================================================
#                 סעיף 4 - עיבוד קובץ בהדרגה
# ============================================================

def load_orders_from_file(filepath: str):
    """
    מחולל (Generator) הקורא נתונים מקובץ שורה-שורה וממיר אותם לאובייקטים ללא העמסת הזיכרון
    """
    # שימוש בקבוצה לשמירת מזהים קיימים ומניעת כפילויות במערכת
    seen_ids = set()

    # פתיחת הקובץ לקריאה בקידוד מתאים בצורה מאובטחת
    with open(filepath, 'r', encoding='utf-8') as file:
        # מעבר על כל שורה בקובץ באופן הדרגתי
        for line_number, line in enumerate(file, start=1):
            # ניקוי רווחים מיותרים מהשורה הנוכחית
            line = line.strip()

            # דילוג על שורות ריקות במידה וישנן
            if not line:
                continue

            try:
                # המרת שורת הטקסט אל מילוני נתונים (Dictionaries)
                data = json.loads(line)

                # בדיקה האם המזהה כבר קיים במערכת כדי למנוע כפילות
                if data["id"] in seen_ids:
                    continue

                # המרת המילון לאובייקט בעזרת מתודת מחלקה ייעודית
                order = MarketOrder.from_dict(data)

                # הוספת המזהה לקבוצת המזהים שכבר נבדקו
                seen_ids.add(data["id"])

                # החזרת האובייקט בהדרגה ללא יצירת רשימה מלאה בזיכרון
                yield order

            except json.JSONDecodeError:
                # התעלמות משורות שאינן בפורמט תקין של קובץ הנתונים
                continue
            except ValueError:
                # התעלמות מרשומות שחסרים בהן שדות או שאינן חוקיות
                continue