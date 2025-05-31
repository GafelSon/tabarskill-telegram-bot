# reminder function -> states handler

# main lib
from enum import Enum, auto
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# dependencies lib
from telegram.ext import ContextTypes
from telegram import Update, ReplyKeyboardMarkup


# local lib
from app.utils.jalali import jcal
from app.database.models import RepeatType


class EventState(Enum):
    TITLE = 0
    DESCRIPTION = 1
    DATE = 2
    TIME = 3
    REPEAT = 4
    NOTIFY = 5
    IMAGE = 6
    PREVIEW = 7


class EventInputHandler:
    QUESTIONS = {
        EventState.TITLE: "📌 لطفاً عنوان رویداد را وارد کنید:",
        EventState.DESCRIPTION: "📝 لطفاً توضیحات رویداد را وارد کنید:",
        EventState.DATE: "📅 لطفاً تاریخ رویداد را انتخاب کنید یا به صورت YYYY/MM/DD وارد کنید:",
        EventState.TIME: "⏰ لطفاً ساعت رویداد را به صورت HH:MM وارد کنید:",
        EventState.REPEAT: "🔄 لطفاً نوع تکرار رویداد را انتخاب کنید:",
        EventState.NOTIFY: "🔔 لطفاً تعداد روزهای قبل از رویداد برای یادآوری را وارد کنید:",
        EventState.IMAGE: "🖼️ لطفاً تصویر رویداد را ارسال کنی (یا 'بدون تصویر' را بنویسید):",
        EventState.PREVIEW: "📋 اطلاعات رویداد به شرح زیر است. آیا می‌خواهید آن را ذخیره کنید؟",
    }

    FIELDS = {
        EventState.TITLE: "title",
        EventState.DESCRIPTION: "description",
        EventState.DATE: "date",
        EventState.TIME: "time",
        EventState.REPEAT: "repeat",
        EventState.NOTIFY: "notify_before",
        EventState.IMAGE: "image",
    }

    REPEAT_TYPE_MAP = {
        "بدون تکرار": RepeatType.NONE.value,
        "روزانه": RepeatType.DAILY.value,
        "هفتگی": RepeatType.WEEKLY.value,
        "ماهانه": RepeatType.MONTHLY.value,
        "سالانه": RepeatType.YEARLY.value,
    }

    @staticmethod
    def get_keyboard() -> ReplyKeyboardMarkup:
        """Get the default keyboard for navigation."""
        return ReplyKeyboardMarkup(
            [["قبلی ◀️", "▶️ بعدی"], ["🚫 انصراف"]], resize_keyboard=True
        )

    @staticmethod
    def get_date_keyboard() -> ReplyKeyboardMarkup:
        """Get the keyboard for date selection."""
        today = jcal.gregorian_to_jalali(datetime.now())
        tomorrow = jcal.gregorian_to_jalali(datetime.now() + timedelta(days=1))
        next_week = jcal.gregorian_to_jalali(datetime.now() + timedelta(days=7))

        keyboard = [
            [f"امروز ({today})", f"فردا ({tomorrow})"],
            [f"هفته آینده ({next_week})"],
            ["تقویم جلالی", "تقویم میلادی"],
            ["قبلی ◀️", "▶️ بعدی"],
            ["🚫 انصراف"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_repeat_type_keyboard() -> ReplyKeyboardMarkup:
        """Get the keyboard for repeat type selection."""
        keyboard = [
            ["بدون تکرار", "روزانه"],
            ["هفتگی", "ماهانه"],
            ["سالانه"],
            ["قبلی ◀️", "▶️ بعدی"],
            ["🚫 انصراف"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_notify_keyboard() -> ReplyKeyboardMarkup:
        """Get the keyboard for notification selection."""
        keyboard = [
            ["بدون یادآوری", "1 روز قبل"],
            ["2 روز قبل", "3 روز قبل"],
            ["قبلی ◀️", "▶️ بعدی"],
            ["🚫 انصراف"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_preview_keyboard() -> ReplyKeyboardMarkup:
        """Get the keyboard for preview confirmation."""
        keyboard = [
            ["✅ تأیید و ذخیره"],
            ["قبلی ◀️", "▶️ بعدی"],
            ["🚫 انصراف"],
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @classmethod
    def get_keyboard_for_state(cls, state: EventState) -> ReplyKeyboardMarkup:
        """Get the appropriate keyboard for the given state."""
        if state == EventState.DATE:
            return cls.get_date_keyboard()
        elif state == EventState.REPEAT:
            return cls.get_repeat_type_keyboard()
        elif state == EventState.NOTIFY:
            return cls.get_notify_keyboard()
        elif state == EventState.PREVIEW:
            return cls.get_preview_keyboard()
        return cls.get_keyboard()

    @classmethod
    def generate_preview_message(cls, user_data: Dict[str, Any]) -> str:
        """Generate a preview message of the event details."""
        repeat_type = next(
            (
                k
                for k, v in cls.REPEAT_TYPE_MAP.items()
                if v == user_data.get("repeat", RepeatType.NONE.value)
            ),
            "بدون تکرار",
        )

        notify_text = (
            "بدون یادآوری"
            if user_data.get("notify_before", 0) == 0
            else f"{user_data.get('notify_before')} روز قبل"
        )

        preview = f"""
        📌 {user_data.get('title', '')}

        📝 {user_data.get('description', '')}

        📅 تاریخ: {user_data.get('date', '')}
        ⏰ ساعت: {user_data.get('time', '')}
        """

        return preview

    @classmethod
    async def handle_input(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        current_state: EventState,
        text: str,
    ) -> tuple[EventState, bool]:
        if current_state == EventState.PREVIEW and text == "✅ تأیید و ذخیره":
            return current_state, False
        if text == "قبلی ◀️":
            if current_state == EventState.TITLE:
                return current_state, False
            return EventState(current_state.value - 1), True

        if text == "🚫 انصراف":
            return current_state, False

        if text == "▶️ بعدی":
            if current_state == EventState.PREVIEW:
                return current_state, True
            return EventState(current_state.value + 1), True

        if current_state == EventState.DATE:
            return await cls._handle_date_input(update, context, text)
        elif current_state == EventState.TIME:
            return await cls._handle_time_input(update, context, text)
        elif current_state == EventState.NOTIFY:
            return await cls._handle_notify_input(update, context, text)
        elif current_state == EventState.REPEAT:
            return await cls._handle_repeat_input(update, context, text)
        else:
            if current_state in cls.FIELDS:
                context.user_data[cls.FIELDS[current_state]] = text
            if current_state == EventState.PREVIEW:
                return current_state, True
            return EventState(current_state.value + 1), True

    @classmethod
    async def _handle_date_input(
        cls, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
    ) -> tuple[EventState, bool]:
        if text.startswith("امروز"):
            date_str = datetime.now().strftime("%Y-%m-%d")
            context.user_data[cls.FIELDS[EventState.DATE]] = date_str
            return EventState(EventState.DATE.value + 1), True
        elif text.startswith("فردا"):
            date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            context.user_data[cls.FIELDS[EventState.DATE]] = date_str
            return EventState(EventState.DATE.value + 1), True
        elif text.startswith("هفته آینده"):
            date_str = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            context.user_data[cls.FIELDS[EventState.DATE]] = date_str
            return EventState(EventState.DATE.value + 1), True
        elif text in ["تقویم جلالی", "تقویم میلادی"]:
            context.user_data["date_format"] = (
                "jalali" if text == "تقویم جلالی" else "gregorian"
            )
            await update.message.reply_text(
                f"لطفاً تاریخ را به صورت {'YYYY/MM/DD جلالی' if text == 'تقویم جلالی' else 'YYYY-MM-DD میلادی'} وارد کنید:"
            )
            return EventState.DATE, True
        else:
            try:
                if context.user_data.get("date_format") == "jalali":
                    jalali_date = text.replace("/", "-")
                    gregorian_date = jcal.jalali_to_gregorian(jalali_date)
                    context.user_data[cls.FIELDS[EventState.DATE]] = gregorian_date
                else:
                    datetime.strptime(text, "%Y-%m-%d")
                    context.user_data[cls.FIELDS[EventState.DATE]] = text
                return EventState(EventState.DATE.value + 1), True
            except ValueError:
                await update.message.reply_text(
                    "❌ فرمت تاریخ اشتباه است. لطفاً دوباره وارد کنید."
                )
                return EventState.DATE, True

    @classmethod
    async def _handle_time_input(
        cls, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
    ) -> tuple[EventState, bool]:
        try:
            datetime.strptime(text, "%H:%M")
            context.user_data[cls.FIELDS[EventState.TIME]] = text
            return EventState(EventState.TIME.value + 1), True
        except ValueError:
            await update.message.reply_text("[ ❌ ] ساعت باید به صورت HH:MM باشد.")
            return EventState.TIME, True

    @classmethod
    async def _handle_notify_input(
        cls, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
    ) -> tuple[EventState, bool]:
        if text == "بدون یادآوری":
            context.user_data["notify_before"] = 0
            return EventState(EventState.NOTIFY.value + 1), True
        try:
            days = int(text.split()[0])
            context.user_data["notify_before"] = days
            return EventState(EventState.NOTIFY.value + 1), True
        except ValueError:
            await update.message.reply_text("[ ❌ ] تعداد روزها باید عدد باشد.")
            return EventState.NOTIFY, True

    @classmethod
    async def _handle_repeat_input(
        cls, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
    ) -> tuple[EventState, bool]:
        repeat_value = cls.REPEAT_TYPE_MAP.get(text, RepeatType.NONE.value)
        context.user_data[cls.FIELDS[EventState.REPEAT]] = repeat_value
        return EventState(EventState.REPEAT.value + 1), True
