# reminder handler -> get functions

# main lib
# .
# .

# dependencies lib
from telegram import ReplyKeyboardMarkup

# local lib
from app.utils.jalali import jcal
from app.database.models import RepeatType

# Preinstance
button = ["بعدی", "قبلی", "انصراف"]
repeat = ["بدون تکرار", "روزانه", "هفتگی", "ماهانه", "سالانه"]

(
    EVENT_TITLE,
    EVENT_DESCRIPTION,
    EVENT_DATE,
    EVENT_REPEAT,
    EVENT_IMAGE,
    EVENT_TIME,
) = range(6)

FIELDS = {
    EVENT_TITLE: "title",
    EVENT_DESCRIPTION: "description",
    EVENT_DATE: "date",
    EVENT_TIME: "time",
    EVENT_REPEAT: "repeat",
    EVENT_IMAGE: "image",
}

REPEAT_TYPE_MAP = {
    "بدون تکرار": RepeatType.NONE.value,
    "روزانه": RepeatType.DAILY.value,
    "هفتگی": RepeatType.WEEKLY.value,
    "ماهانه": RepeatType.MONTHLY.value,
    "سالانه": RepeatType.YEARLY.value,
}

QUESTIONS = {
    EVENT_TITLE: "✨ عنوان رویداد\n\nلطفاً یک عنوان واضح برای رویداد وارد کنید:\nمثال: «امتحان پایان ترم طراحی الگوریتم»",
    EVENT_DESCRIPTION: "📋 توضیحات رویداد\n\nلطفاً جزئیات رویداد را شرح دهید:\nمثال: «امتحان فصل‌های ۳ و ۴ - سالن اصلی»",
    EVENT_DATE: "🗓️ تاریخ رویداد\n\nلطفاً از دکمه‌های زیر برای انتخاب تاریخ استفاده کنید:\n(یا به صورت ۱۴۰۳/۰۵/۱۵ وارد نمایید)",
    EVENT_TIME: "⏱️ ساعت رویداد\n\nلطفاً ساعت را به فرمت ۲۴ ساعته وارد کنید:\nمثال: ۱۴:۳۰ یا ۰۸:۰۰",
    EVENT_REPEAT: "🔄 تکرار رویداد\n\nآیا این رویداد تکرار می‌شود؟\nلطفاً نوع تکرار را انتخاب کنید:",
    EVENT_IMAGE: "🖼️ تصویر رویداد\n\nمی‌توانید یک تصویر مرتبط ارسال کنید\nیا عبارت «بدون تصویر» را تایپ نمایید:",
}


def keyboard():
    return ReplyKeyboardMarkup(
        [[f"◀️ {button[0]}", f"{button[1]} ▶️"], [f"🚫 {button[2]}"]],
        resize_keyboard=True,
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
    today = jcal.gregorian_to_jalali(datetime.now()).strftime("%Y/%m/%d")
    tomorrow = jcal.gregorian_to_jalali(datetime.now() + timedelta(days=1)).strftime(
        "%Y/%m/%d"
    )
    aWeak = jcal.gregorian_to_jalali(datetime.now() + timedelta(days=7)).strftime(
        "%Y/%m/%d"
    )

    # ![TODO] make keyboard here for select date and fomrat them
    keyboard = [
        [f"امروز ({today})", f"فردا ({tomorrow})"],
        [f"هفته آینده ({next_week})"],
        [f"◀️ {button[0]}", f"{button[1]} ▶️"],
        [f"❌ {button[2]}"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
