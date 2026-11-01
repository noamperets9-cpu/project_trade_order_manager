import pytest

from project_name import console_ui as ui


# ============================================================
#     סידור עברית לתצוגה בטרמינל שלא תומך בכיווניות (RTL)
# ============================================================

@pytest.fixture
def bidi_on(monkeypatch):
    monkeypatch.setattr(ui, "USE_BIDI", True)


def test_hebrew_is_reordered_for_display(bidi_on):
    # הטרמינל מציג משמאל לימין, ולכן התווים נשלחים בסדר תצוגה (הפוך)
    assert ui.rtl("ניתוח מנהל הסיכונים") == "םינוכיסה להנמ חותינ"


def test_english_and_numbers_keep_their_order(bidi_on):
    displayed = ui.rtl("נטענו 15 פקודות, למשל ORD1001")
    assert "15" in displayed
    assert "ORD1001" in displayed


def test_text_without_hebrew_is_unchanged(bidi_on):
    assert ui.rtl("[asyncio] 1.51s app.log") == "[asyncio] 1.51s app.log"


def test_color_codes_stay_around_their_text(bidi_on):
    painted = ui.GREEN + "בוצעה" + ui.RESET
    assert ui.rtl(painted) == ui.GREEN + "העצוב" + ui.RESET


def test_edge_spaces_stay_in_place(bidi_on):
    assert ui.rtl("  שלום ") == "  םולש "


def test_disabled_bidi_keeps_logical_order(monkeypatch):
    # למשל כשהפלט מופנה לקובץ: שם הטקסט צריך להישמר בסדר הרגיל
    monkeypatch.setattr(ui, "USE_BIDI", False)
    assert ui.rtl("ניתוח מנהל הסיכונים") == "ניתוח מנהל הסיכונים"
