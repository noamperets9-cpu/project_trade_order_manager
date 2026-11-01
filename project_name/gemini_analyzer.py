import logging

from .config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TIMEOUT_MS

try:
    from google import genai
    from google.genai import errors, types
except ImportError:  # בלי הספרייה המחלקה עדיין נטענת, והניתוח פשוט לא זמין
    genai = errors = types = None

logger = logging.getLogger(__name__)

# ============================================================
#     הרחבה - ניתוח AI וצ'אט על תוצאות ההרצה (Google Gemini)
# ============================================================
# המחלקה רק מסכמת ומסבירה: היא לא משנה פקודות, יתרות או החלטות אישור.
# הלקוח של Gemini מועבר מבחוץ (Dependency Injection), כך שבבדיקות אפשר להעביר לקוח מדומה בלי רשת.
# כל כשל בקריאה ל-API (מפתח שגוי, מודל לא זמין, שגיאת רשת) מוחזר כ-None ונרשם בלוג,
# כדי שהדגמת המערכת לא תיפול בגלל שלב שהוא תוספת בלבד.

SYSTEM_INSTRUCTION = (
    "אתה אנליסט סיכונים בחדר מסחר. ענה בעברית ובקצרה. "
    "כל מספר או נתון על הפקודות, המדיניות והיתרות חייב להגיע מדוח ההרצה, ואל תמציא נתונים שלא מופיעים בו. "
    "מותר ורצוי לנתח, להשוות, להסביר ולתת שיקול דעת מקצועי על סמך הנתונים. "
    "כתוב טקסט רגיל לטרמינל, ללא Markdown (בלי ** או #)."
)


class GeminiAnalyzer:
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL, client=None):
        """ מאתחל את המנתח. אם לא הועבר לקוח, נוצר לקוח אמיתי של google-genai לפי המפתח """
        self.model = model
        self.unavailable_reason = ""  # למה אין חיבור, כדי להציג למשתמש סיבה מדויקת
        self.client = client if client is not None else self._create_client(api_key)
        self._chat = None
        self.last_usage = None  # ספירת הטוקנים של התשובה האחרונה (נשלחו / התקבלו)

    def _create_client(self, api_key: str):
        """ יוצר לקוח של Gemini, או מחזיר None (ושומר את הסיבה) אם אין מפתח או שהספרייה לא מותקנת """
        if genai is None:
            self.unavailable_reason = "הספרייה google-genai לא מותקנת (הריצו: pip install -e .)"
        elif not api_key:
            self.unavailable_reason = "לא הוגדר GEMINI_API_KEY (העתיקו את .env.example ל-.env והוסיפו מפתח)"
        else:
            try:
                return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=GEMINI_TIMEOUT_MS))
            except Exception as error:
                self.unavailable_reason = f"יצירת החיבור ל-Gemini נכשלה ({type(error).__name__})"
                logger.error("יצירת לקוח Gemini נכשלה: %s", error)
                return None
        logger.warning("%s - שלב ניתוח ה-AI ידולג", self.unavailable_reason)
        return None

    @property
    def is_available(self) -> bool:
        """ האם אפשר לפנות ל-Gemini (יש לקוח תקין) """
        return self.client is not None

    # ---------- בניית הדוח ----------

    @staticmethod
    def build_report(orders: list, results_by_policy: dict, balances: dict,
                     rate: float, initial_budget: float) -> str:
        """ בונה דוח טקסט מנתוני ההרצה: פקודות, החלטות האישור לפי מדיניות והיתרות שנותרו """
        lines = [
            f"תקציב התחלתי: {initial_budget:,.2f} ש\"ח | שער דולר-שקל: {rate:.4f}",
            "",
            "פקודות:",
        ]
        for order in orders:
            if order.get_priority() == 1:
                kind = f"Stop-Loss, מחיר עצירה ${order.stop_price:,.2f}"
            else:
                kind = "Market"
            lines.append(f"- {order.order_id}: {order.action} {order.quantity} {order.symbol} "
                         f"במחיר ${order.price:,.2f} ({kind})")

        for policy_name, results in results_by_policy.items():
            approved = [r.order_id for r in results if r.approved]
            rejected = [f"{r.order_id} ({r.reason})" for r in results if not r.approved]
            lines += [
                "",
                f"מדיניות: {policy_name}",
                f"  אושרו ({len(approved)}): {', '.join(approved) or 'אין'}",
                f"  נדחו ({len(rejected)}): {', '.join(rejected) or 'אין'}",
                f"  יתרה שנותרה: {balances[policy_name]:,.2f} ש\"ח",
            ]

        return "\n".join(lines)

    # ---------- קריאות ל-API ----------

    def summarize(self, report: str):
        """ מבקש מ-Gemini סיכום של הדוח והמלצה למנהל הסיכונים. מחזיר טקסט או None """
        if not self.is_available:
            return None
        prompt = (
            "נתח בעד 8 שורות את תוצאות בקרת התקציב הבאות. התייחס לניצול התקציב, להבדל בין המדיניות, "
            "לפקודות Stop-Loss שדורשות תשומת לב, ותן המלצה אחת למנהל הסיכונים.\n\n" + report
        )
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self._make_config(SYSTEM_INSTRUCTION),
            )
            self.last_usage = getattr(response, "usage_metadata", None)
            return self._extract_text(response)
        except Exception as error:
            self._log_api_error("סיכום הדוח", error)
            return None

    def start_chat(self, report: str) -> bool:
        """ פותח שיחה חדשה עם Gemini, שהדוח מוזן אליה כהקשר. מחזיר True אם השיחה נפתחה """
        if not self.is_available:
            return False
        try:
            self._chat = self.client.chats.create(
                model=self.model,
                config=self._make_config(f"{SYSTEM_INSTRUCTION}\n\nדוח ההרצה:\n{report}"),
            )
            return True
        except Exception as error:
            self._log_api_error("פתיחת הצ'אט", error)
            self._chat = None
            return False

    def ask(self, question: str):
        """ שולח שאלה בשיחה הפתוחה ומחזיר את התשובה, או None בכשל """
        if self._chat is None:
            raise RuntimeError("יש לפתוח שיחה עם start_chat לפני ששולחים שאלה")
        try:
            response = self._chat.send_message(question)
            self.last_usage = getattr(response, "usage_metadata", None)
            return self._extract_text(response)
        except Exception as error:
            self._log_api_error("שאלה בצ'אט", error)
            return None

    def history(self) -> list:
        """ מחזיר את היסטוריית השיחה כרשימה של (תפקיד, טקסט) - user או model """
        if self._chat is None:
            return []
        try:
            return [(msg.role, msg.parts[0].text) for msg in self._chat.get_history()
                    if msg.parts and msg.parts[0].text]
        except Exception as error:
            self._log_api_error("קריאת היסטוריית הצ'אט", error)
            return []

    # ---------- עזר ----------

    @staticmethod
    def _make_config(system_instruction: str):
        """ הגדרות הבקשה: הנחיית המערכת (types.GenerateContentConfig, או מילון כשהספרייה חסרה) """
        if types is None:
            return {"system_instruction": system_instruction}
        return types.GenerateContentConfig(system_instruction=system_instruction)

    @staticmethod
    def _extract_text(response):
        """ מחלץ את טקסט התשובה. תשובה ריקה נחשבת לכשל """
        text = (getattr(response, "text", None) or "").strip()
        if not text:
            logger.error("Gemini החזיר תשובה ריקה")
            return None
        logger.info("התקבלה תשובה מ-Gemini (%d תווים)", len(text))
        return text

    @staticmethod
    def _log_api_error(action: str, error: Exception):
        """ רושם בלוג את סוג הכשל: שגיאת API (עם קוד) או כשל כללי (רשת וכו') """
        if errors is not None and isinstance(error, errors.APIError):
            logger.error("%s נכשל - שגיאת API %s: %s", action, error.code, error.message)
        else:
            logger.error("%s נכשל - %s: %s", action, type(error).__name__, error)
