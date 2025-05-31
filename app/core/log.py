class Emoji:
    ERROR = "❌"
    SUCCESS = "✅"
    WARNING = "⚠️"
    QUESTION = "❓"
    INFO = "ℹ️"

    # Additional commonly used emojis
    CHECKMARK = "✔️"
    CROSS_MARK = "❌"
    HOURGLASS = "⌛"
    LOCK = "🔒"
    BELL = "🔔"
    STAR = "⭐"
    HEART = "❤️"
    THUMBS_UP = "👍"
    THUMBS_DOWN = "👎"
    CELEBRATE = "🎉"

    # Formatting
    BULLET = "•"
    ARROW_RIGHT = "→"


def internal_error() -> str:
    """Internal error message (Fn)"""
    text = "خطایی رخ داد. لطفا بعدا دوباره تلاش کنید."
    return f"[ {Emoji.ERROR} ] {text}"


def call_error() -> str:
    """Call error message (Fn)"""
    text = "در حال حاضر دانشگاهی در سیستم ثبت نشده است. لطفاً با پشتیبانی تماس بگیرید."
    return f"[ {Emoji.ERROR} ] {text}"


def start_warning() -> str:
    """Start warning message (Fn)"""
    text = "خطایی رخ داده است. لطفاً با /start دوباره تلاش کنید."
    return f"[ {Emoji.WARNING} ] {text}"


def celebration_info() -> str:
    """Celebration message (Fn)"""
    text = "پروفایل شما با موفقیت تکمیل شد!"
    return f"[ {Emoji.CELEBRATE} ] {text}"


def accessibility_error() -> str:
    """Accessibility error message"""
    text = "شما دسترسی لازم برای ایجاد رویدادهای دانشگاهی را ندارید!"
    return f"[ {Emoji.ERROR} ] {text}"


def channel_warning() -> str:
    """Channel error message"""
    text = "هنوز عضو کانال نشده‌اید! لطفاً ابتدا در کانال عضو شوید."
    return f"[ {Emoji.WARNING} ] {text}"


def cancel_alert(func) -> str:
    """Cencel Warning message (Fn)"""
    text = f"عملیات {func} لغو شد"
    return f"[ {Emoji.ERROR} ] {text}"


def ask_profile_completion(id: int) -> str:
    """Ask profile completion message (Fn)"""
    match id:
        case 1:
            return f"{Emoji.QUESTION} لطفاً دانشگاه خود را انتخاب کنید."
        case 2:
            return f"{Emoji.QUESTION} لطفاً دانشکده خود را انتخاب کنید."
        case 3:
            return f"{Emoji.QUESTION} لطفاً رشته تحصیلی خود را انتخاب کنید."
        case 4:
            return f"{Emoji.QUESTION} لطفاً نقش خود را انتخاب کنید."
