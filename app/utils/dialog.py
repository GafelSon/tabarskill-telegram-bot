# Utils -> dialog module

# main lib
import re
import difflib
import json
import os

KEYWORDS = {
    "سلام": ["سلام", "سلام ربات", "سلام خوبی", "درود", "سلام علیکم"],
    "خداحافظ": ["خداحافظ", "بای", "فعلاً", "بعداً می‌بینمت"],
    "راهنما": ["کمک", "راهنما", "چی کار می‌کنی", "چه کاری بلدی؟"],
    "معرفی": ["تو کی هستی", "اسمت چیه", "چی هستی", "چه کسی هستی"],
}

DEFAULT_RESPONSES = {
    "سلام": "سلام! حالت چطوره؟ 🤖",
    "خداحافظ": "فعلاً! اگه کاری داشتی بازم پیام بده 😎",
    "راهنما": "برای راهنما می‌تونی گزینه «📖 راهنما» رو انتخاب کنی یا بنویسی: راهنما",
    "معرفی": "من ربات دستیار دانشگاهی‌ام. برای کمک بهت اینجام 🎓",
    "default": "متوجه منظورت نشدم... می‌تونی یکی از گزینه‌های منو رو امتحان کنی یا «کمک» بنویسی 🤔",
}


def load_responses():
    responses_file = os.path.join(
        os.path.dirname(__file__), "..", "data", "responses.json"
    )

    try:
        if os.path.exists(responses_file):
            with open(responses_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"خطا در بارگذاری فایل پاسخ‌ها: {e}")

    responses = {}
    for key in KEYWORDS:
        responses[key] = {"phrases": KEYWORDS[key], "response": DEFAULT_RESPONSES[key]}

    return responses


def similar(text, candidates):
    match = difflib.get_close_matches(text, candidates, n=1, cutoff=0.7)
    return match[0] if match else None


def simple_dialog_manager(user_input: str) -> str:
    text = user_input.strip().lower()
    responses = load_responses()

    for key, data in responses.items():
        for phrase in data["phrases"]:
            if phrase in text:
                return data["response"]

    all_phrases = []
    phrase_to_key = {}

    for key, data in responses.items():
        for phrase in data["phrases"]:
            all_phrases.append(phrase)
            phrase_to_key[phrase] = key

    similar_phrase = similar(text, all_phrases)
    if similar_phrase:
        key = phrase_to_key[similar_phrase]
        return responses[key]["response"]

    return DEFAULT_RESPONSES["default"]


if __name__ == "__main__":
    test_dialog_manager()
