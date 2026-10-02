# repository.py
import json
from models import MarketOrder

def load_orders_from_file(filepath: str) -> list:
    """
    קורא נתוני פקודות מסחר מקובץ JSONL וממיר אותם לאובייקטים.
    הקריאה מתבצעת שורה-שורה (Lazy) כדי לא להעמיס על הזיכרון.
    """
    orders = []
    seen_ids = set() # שימוש בקבוצה (Set) לבדיקת כפילויות יעילה

    with open(filepath, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue # דילוג על שורות ריקות
            
            try:
                # המרת השורה ממחרוזת JSON למילון (dict)
                data = json.loads(line)
                
                # בדיקת כפילות מזהים
                if data["id"] in seen_ids:
                    print(f"שגיאה בשורה {line_number}: המזהה {data['id']} כבר קיים. מדלג.")
                    continue
                
                # המרה לאובייקט באמצעות הבנאי האלטרנטיבי שיצרנו בחלק ב'
                order = MarketOrder.from_dict(data)
                
                orders.append(order)
                seen_ids.add(data["id"])
                
            except json.JSONDecodeError:
                print(f"שגיאת פורמט JSON בשורה {line_number}. מדלג.")
            except ValueError as e:
                # תופס שגיאות חסר בשדות או ולידציה של מחיר/כמות
                print(f"נתונים לא חוקיים בשורה {line_number}: {e}")
                
    return orders