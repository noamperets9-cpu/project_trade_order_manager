from types import SimpleNamespace

import pytest
from google.genai import errors

from project_name.gemini_analyzer import GeminiAnalyzer
from project_name.models import MarketOrder, StopLossOrder
from project_name.services import ApprovalResult


# ---------- לקוח Gemini מדומה (ללא רשת) ----------

class FakeChat:
    def __init__(self, answers):
        self.answers = list(answers)
        self.questions = []

    def send_message(self, message):
        self.questions.append(message)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        usage = SimpleNamespace(prompt_token_count=len(message), candidates_token_count=len(answer))
        return SimpleNamespace(text=answer, usage_metadata=usage)

    def get_history(self):
        def msg(role, text):
            return SimpleNamespace(role=role, parts=[SimpleNamespace(text=text)])
        return [msg("user", "מה היתרה?"), msg("model", "תשובה 1")]


class FakeClient:
    def __init__(self, text=None, error=None, chat_answers=(), chat_error=None):
        self.calls = []
        self.chat_configs = []
        self.chat = FakeChat(chat_answers)
        self.models = SimpleNamespace(generate_content=self._generate)
        self.chats = SimpleNamespace(create=self._create_chat)
        self._text, self._error, self._chat_error = text, error, chat_error

    def _generate(self, model, contents, config=None):
        self.calls.append((model, contents))
        if self._error:
            raise self._error
        return SimpleNamespace(text=self._text)

    def _create_chat(self, model, config=None):
        if self._chat_error:
            raise self._chat_error
        self.chat_configs.append(config)
        return self.chat


def api_error(code=404):
    return errors.ClientError(code, {"error": {"code": code, "message": "model not found", "status": "NOT_FOUND"}})


@pytest.fixture
def report():
    orders = [
        MarketOrder("O1", "AAPL", "Buy", 10, 100.0),
        StopLossOrder("S1", "TSLA", "Sell", 5, 200.0, stop_price=190.0),
    ]
    results = {"Full": [ApprovalResult("O1", True, 3700.0, "אושרה ושוריין תקציב")],
               "Strict": [ApprovalResult("O1", False, 3700.0, "נדחתה לפי מדיניות התקציב")]}
    balances = {"Full": 6300.0, "Strict": 10_000.0}
    return GeminiAnalyzer.build_report(orders, results, balances, rate=3.7, initial_budget=10_000)


# ---------- בניית הדוח ----------

def test_report_contains_run_data(report):
    assert "O1: Buy 10 AAPL" in report
    assert "Stop-Loss, מחיר עצירה $190.00" in report
    assert "3.7000" in report
    assert "יתרה שנותרה: 6,300.00" in report
    assert "נדחו (1): O1 (נדחתה לפי מדיניות התקציב)" in report


# ---------- זמינות ----------

@pytest.mark.parametrize("missing_key", [None, ""])  # os.getenv מחזיר None כשאין מפתח
def test_no_api_key_means_not_available(missing_key):
    analyzer = GeminiAnalyzer(api_key=missing_key)
    assert analyzer.is_available is False
    assert "No API key detected" in analyzer.unavailable_reason
    assert analyzer.summarize("report") is None
    assert analyzer.start_chat("report") is False


def test_simulated_summary_works_without_key_or_network():
    results = {"Full": [ApprovalResult("O1", True, 4000.0, ""), ApprovalResult("O2", False, 9000.0, "")],
               "Strict": [ApprovalResult("O1", False, 4000.0, ""), ApprovalResult("O2", False, 9000.0, "")]}
    balances = {"Full": 6000.0, "Strict": 10_000.0}

    lines = GeminiAnalyzer.simulated_summary(results, balances, initial_budget=10_000)

    assert lines[0] == "Full: אושרו 1 מתוך 2 פקודות, נוצלו 4,000.00 ש\"ח (40% מהתקציב)"
    assert lines[-1] == "היתרה הגבוהה ביותר נשארה במדיניות: Strict (10,000.00 ש\"ח)"


# ---------- סיכום ----------

def test_summarize_sends_report_to_model(report):
    client = FakeClient(text="  סיכום לדוגמה  ")
    analyzer = GeminiAnalyzer(model="gemini-2.5-flash", client=client)

    assert analyzer.summarize(report) == "סיכום לדוגמה"
    [(model, prompt)] = client.calls
    assert model == "gemini-2.5-flash"
    assert report in prompt


@pytest.mark.parametrize("error", [api_error(404), ConnectionError("down")])
def test_summarize_failure_returns_none_instead_of_crashing(error):
    analyzer = GeminiAnalyzer(client=FakeClient(error=error))
    assert analyzer.summarize("report") is None


def test_empty_response_returns_none():
    assert GeminiAnalyzer(client=FakeClient(text="")).summarize("report") is None


# ---------- צ'אט ----------

def test_chat_keeps_report_as_context_and_answers(report):
    client = FakeClient(chat_answers=["תשובה 1", "תשובה 2"])
    analyzer = GeminiAnalyzer(client=client)

    assert analyzer.start_chat(report) is True
    assert report in client.chat_configs[0].system_instruction
    assert analyzer.ask("מה היתרה?") == "תשובה 1"
    assert analyzer.ask("ולמה?") == "תשובה 2"
    # אותה שיחה משמשת לכל השאלות, כך שהמודל זוכר את ההקשר
    assert client.chat.questions == ["מה היתרה?", "ולמה?"]


def test_chat_records_token_usage_and_history():
    analyzer = GeminiAnalyzer(client=FakeClient(chat_answers=["תשובה 1"]))
    assert analyzer.history() == []  # לפני פתיחת שיחה

    analyzer.start_chat("report")
    analyzer.ask("מה היתרה?")

    assert analyzer.last_usage.prompt_token_count == len("מה היתרה?")
    assert analyzer.last_usage.candidates_token_count == len("תשובה 1")
    assert analyzer.history() == [("user", "מה היתרה?"), ("model", "תשובה 1")]


def test_chat_api_error_returns_none_and_chat_stays_usable():
    analyzer = GeminiAnalyzer(client=FakeClient(chat_answers=[api_error(503), "עובד שוב"]))
    analyzer.start_chat("report")

    assert analyzer.ask("שאלה") is None
    assert analyzer.ask("שאלה") == "עובד שוב"


def test_chat_creation_failure_returns_false():
    analyzer = GeminiAnalyzer(client=FakeClient(chat_error=api_error(404)))
    assert analyzer.start_chat("report") is False


def test_ask_before_start_chat_raises():
    with pytest.raises(RuntimeError):
        GeminiAnalyzer(client=FakeClient()).ask("שאלה")
