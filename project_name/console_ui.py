import os
import re
import shutil
import sys
import textwrap

try:
    from bidi import get_display
except ImportError:  # בלי python-bidi העברית מודפסת כמו שהיא
    get_display = None

# ============================================================
#        כלי עזר להצגה קריאה וצבעונית של הפלט בקונסול
# ============================================================
# צבעים בעזרת קודי ANSI (נתמכים ב-PyCharm ובטרמינל).
# אפשר לכבות צבעים עם משתנה הסביבה NO_COLOR=1.
# הערה: בטבלאות הכותרות באנגלית, כי שני תאים בעברית זה ליד זה
# מתהפכים בתצוגה של הקונסול ושוברים את היישור.
#
# כיווניות (RTL): הטרמינל של VS Code ו-PyCharm לא תומך בעברית מימין לשמאל,
# ומציג כל שורה משמאל לימין - ולכן העברית נראית הפוכה.
# המחרוזות בקוד נשמרות בסדר הרגיל, והן מסודרות לתצוגה (rtl) רק ברגע ההדפסה.
# TERMINAL_BIDI=auto (ברירת מחדל): רק כשהפלט הוא טרמינל, לא כשהוא מופנה לקובץ.
# TERMINAL_BIDI=off: לטרמינל שתומך בעברית בעצמו. TERMINAL_BIDI=on: תמיד.

USE_COLOR = "NO_COLOR" not in os.environ
WIDTH = 72

_BIDI_MODE = os.environ.get("TERMINAL_BIDI", "auto").lower()
USE_BIDI = get_display is not None and (
    _BIDI_MODE == "on" or (_BIDI_MODE == "auto" and sys.stdout.isatty())
)

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
_ANSI_SPLIT = re.compile(r"(\033\[[0-9;]*m)")
_HEBREW = re.compile(r"[֐-׿]")


def paint(text, *styles) -> str:
    """ צובע טקסט בסגנונות שהתקבלו (אם הצבעים מופעלים) """
    if not USE_COLOR or not styles:
        return str(text)
    return "".join(styles) + str(text) + RESET


def visible_len(text: str) -> int:
    """ אורך הטקסט כפי שהוא נראה על המסך, בלי קודי הצבע """
    return len(_ANSI_PATTERN.sub("", str(text)))


# ---------- כיווניות (RTL) ----------

def _rtl_segment(segment: str) -> str:
    """ מסדר קטע טקסט אחד (בלי קודי צבע) לתצוגה, ושומר את הרווחים שבקצוות במקומם """
    core = segment.strip(" ")
    if not _HEBREW.search(core):
        return segment
    start = segment.index(core)
    return segment[:start] + get_display(core) + segment[start + len(core):]


def rtl(text) -> str:
    """
    מחזיר את הטקסט בסדר תצוגה לטרמינל שלא תומך בכיווניות.
    כל קטע בין קודי הצבע מסודר בנפרד, כך שהצבעים, האנגלית והמספרים נשארים במקומם.
    """
    text = str(text)
    if not USE_BIDI or not _HEBREW.search(text):
        return text
    parts = _ANSI_SPLIT.split(text)
    return "".join(part if _ANSI_PATTERN.fullmatch(part) else _rtl_segment(part) for part in parts)


def ask(prompt: str) -> str:
    """ input() עם שאלה שמוצגת בכיוון הנכון """
    return input(rtl(prompt))


def _print_message(prefix: str, message, *styles):
    """
    מדפיס הודעה אחרי תחילית (אייקון), ומפצל הודעה ארוכה לכמה שורות לפני הסידור,
    כדי שכל שורה בטרמינל תיקרא בסדר הנכון.
    """
    message = str(message)
    width = shutil.get_terminal_size((100, 20)).columns - visible_len(prefix) - 1
    lines = [message]
    if USE_BIDI and "\033" not in message and len(message) > width > 20:
        lines = textwrap.wrap(message, width)
    for i, line in enumerate(lines):
        lead = prefix if i == 0 else " " * visible_len(prefix)
        print(lead + paint(rtl(line), *styles))


# ---------- כותרות ----------

def banner(title: str, subtitle: str = ""):
    """ כותרת ראשית בתחילת ההרצה """
    line = paint("═" * WIDTH, CYAN)
    print(line)
    print("  " + paint(rtl(title), BOLD, CYAN))
    if subtitle:
        print("  " + paint(rtl(subtitle), DIM))
    print(line)


def section(number: int, title: str, concept: str = ""):
    """ כותרת לשלב בהדגמה, עם שם המושג שמודגם """
    print()
    head = paint(f" {number} ", BOLD, "\033[46m", "\033[30m") + " " + paint(rtl(title), BOLD)
    if concept:
        head += "  " + paint(f"[{concept}]", MAGENTA)
    print(head)
    print(paint("─" * WIDTH, DIM))


def footer(text: str):
    """ שורת סיום """
    print()
    print(paint("═" * WIDTH, CYAN))
    print("  " + paint(rtl(text), BOLD, GREEN))
    print(paint("═" * WIDTH, CYAN))


# ---------- שורות הודעה ----------

def ok(message: str):
    _print_message("  " + paint("✔", GREEN, BOLD) + " ", message)


def info(message: str):
    _print_message("  " + paint("•", CYAN) + " ", message)


def warn(message: str):
    _print_message("  " + paint("!", YELLOW, BOLD) + " ", message, YELLOW)


def error(message: str):
    _print_message("  " + paint("✘", RED, BOLD) + " ", message, RED)


def note(message: str):
    _print_message("    ", message, DIM)


def plain(message: str = ""):
    """ שורה רגילה בלי אייקון """
    _print_message("  ", message)


def kv(label: str, value):
    """ שורת "שם: ערך" עם הדגשת הערך """
    print("  " + paint("•", CYAN) + " " + rtl(f"{label}:") + " " + paint(rtl(value), BOLD))


def subheading(text: str):
    print()
    print("  " + paint(rtl(text), BOLD, YELLOW))


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
            text = (" " * pad + rtl(cell)) if align[i] == "r" else (rtl(cell) + " " * pad)
            parts.append(paint(text, style) if style else text)
        return "  " + paint("│", DIM).join(f" {p} " for p in parts)

    border = "  " + paint("┼".join("─" * (w + 2) for w in widths), DIM)
    print(fmt(headers, BOLD))
    print(border)
    for row in rows:
        print(fmt(row))
