import os
import re

# ============================================================
#        כלי עזר להצגה קריאה וצבעונית של הפלט בקונסול
# ============================================================
# ללא ספריות חיצוניות: צבעים בעזרת קודי ANSI (נתמכים ב-PyCharm ובטרמינל).
# אפשר לכבות צבעים עם משתנה הסביבה NO_COLOR=1.
# הערה: בטבלאות הכותרות באנגלית, כי שני תאים בעברית זה ליד זה
# מתהפכים בתצוגה של הקונסול ושוברים את היישור.

USE_COLOR = "NO_COLOR" not in os.environ
WIDTH = 72

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

_ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")


def paint(text, *styles) -> str:
    """ צובע טקסט בסגנונות שהתקבלו (אם הצבעים מופעלים) """
    if not USE_COLOR or not styles:
        return str(text)
    return "".join(styles) + str(text) + RESET


def visible_len(text: str) -> int:
    """ אורך הטקסט כפי שהוא נראה על המסך, בלי קודי הצבע """
    return len(_ANSI_PATTERN.sub("", str(text)))


# ---------- כותרות ----------

def banner(title: str, subtitle: str = ""):
    """ כותרת ראשית בתחילת ההרצה """
    line = paint("═" * WIDTH, CYAN)
    print(line)
    print("  " + paint(title, BOLD, CYAN))
    if subtitle:
        print("  " + paint(subtitle, DIM))
    print(line)


def section(number: int, title: str, concept: str = ""):
    """ כותרת לשלב בהדגמה, עם שם המושג שמודגם """
    print()
    head = paint(f" {number} ", BOLD, "\033[46m", "\033[30m") + " " + paint(title, BOLD)
    if concept:
        head += "  " + paint(f"[{concept}]", MAGENTA)
    print(head)
    print(paint("─" * WIDTH, DIM))


def footer(text: str):
    """ שורת סיום """
    print()
    print(paint("═" * WIDTH, CYAN))
    print("  " + paint(text, BOLD, GREEN))
    print(paint("═" * WIDTH, CYAN))


# ---------- שורות הודעה ----------

def ok(message: str):
    print("  " + paint("✔", GREEN, BOLD) + " " + message)


def info(message: str):
    print("  " + paint("•", CYAN) + " " + message)


def warn(message: str):
    print("  " + paint("!", YELLOW, BOLD) + " " + paint(message, YELLOW))


def error(message: str):
    print("  " + paint("✘", RED, BOLD) + " " + paint(message, RED))


def note(message: str):
    print("    " + paint(message, DIM))


def kv(label: str, value):
    """ שורת "שם: ערך" עם הדגשת הערך """
    print("  " + paint("•", CYAN) + " " + f"{label}: " + paint(value, BOLD))


def subheading(text: str):
    print()
    print("  " + paint(text, BOLD, YELLOW))


# ---------- עיצוב ערכים ----------

def usd(amount: float) -> str:
    return f"${amount:,.2f}"


def ils(amount: float) -> str:
    return f"₪{amount:,.2f}"


def tag_simulated() -> str:
    return paint("[מדומה]", YELLOW, BOLD)


def tag_live() -> str:
    return paint("[אמיתי]", GREEN, BOLD)


# ---------- טבלה ----------

def table(headers: list, rows: list, align: str = ""):
    """
    מדפיס טבלה מיושרת.
    align: מחרוזת עם תו לכל עמודה - 'l' לשמאל, 'r' לימין (למספרים).
    """
    align = align.ljust(len(headers), "l")
    widths = [visible_len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], visible_len(cell))

    def fmt(cells, style=None):
        parts = []
        for i, cell in enumerate(cells):
            pad = widths[i] - visible_len(cell)
            text = (" " * pad + str(cell)) if align[i] == "r" else (str(cell) + " " * pad)
            parts.append(paint(text, style) if style else text)
        return "  " + paint("│", DIM).join(f" {p} " for p in parts)

    border = "  " + paint("┼".join("─" * (w + 2) for w in widths), DIM)
    print(fmt(headers, BOLD))
    print(border)
    for row in rows:
        print(fmt(row))
