# reminder handler -> get functions

# main lib

# dependencies lib
from telegram import ReplyKeyboardMarkup

# local lib

# Preinstance
button = ["بعدی", "قبلی", "لغو"]
repeat = ["بدون تکرار", "روزانه", "هفتگی", "ماهانه", "سالانه"]
notif = ["بدون یادآوری", "1 روز قبل", "2 روز قبل"]


def keyboard():
    return ReplyKeyboardMarkup(
        [f"◀️ {button[0]}", f"{button[1]} ▶️", [f"❌ {button[2]}"]], resize_keyboard=True
    )


def repeat_type_keyboard():
    keyboard = [
        [repeat[0], repeat[1]],
        [repeat[2], repeat[3]],
        [repeat[4]],
        [f"◀️ {button[0]}", f"{button[1]} ▶️"],
        [f"❌ {button[2]}"],
    ]


def date_keyboard():
    today = jcal.gregorian_to_jalali(datetime.now())
    tomorrow = jcal.gregorian_to_jalali(datetime.now() + timedelta(days=1))
    aWeak = jcal.gregorian_to_jalali(datetime.now() + timedelta(days=7))

    # ![TODO] make keyboard here for select date and fomrat them
    keyboard = [
        [f"امروز ({today})", f"فردا ({tomorrow})"],
        [f"هفته آینده ({next_week})"],
        [f"◀️ {button[0]}", f"{button[1]} ▶️"],
        [f"❌ {button[2]}"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def notify():
    keyboard = [
        [notif[0]],
        [notif[1], notif[2]],
        [f"◀️ {button[0]}", f"{button[1]} ▶️"],
        [f"❌ {button[2]}"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
