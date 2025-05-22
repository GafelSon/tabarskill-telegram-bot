# start handler function -> about

# dependencies lib
from telegram import Update
from telegram.ext import ContextTypes

# local lib
from app.core.logger import logger
from app.utils.escape import markdownES

# config logger
logger = logger(__name__)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Handle the about callback """
    query = update.callback_query
    await query.answer()

    header = f">درباره من\n\n\n"
    onboarding = (
        f"من سهیل فولادوندی هستم؛ برنامه‌نویس، دانشجوی عضو اصلی انجمن علمی کامپیوتر دانشگاه امام محمد باقر (ع) ساری 💻📚\n\n"
        f"این ربات هوشمند، نتیجه‌ی تلاش‌های شخصی منه و فعلاً دارم به‌تنهایی روی توسعه و ارتقاش کار می‌کنم 🤖✨ اما واقعاً دوست دارم افراد خلاق، باانگیزه و خوش‌ذوق به تیم من اضافه بشن تا بتونیم این پروژه رو با هم به سطح بالاتری برسونیم 🚀💡\n\n"
        f"اگر پیشنهادی داری، یا به مشکلی برخوردی، خوشحال می‌شم در جریانم بذاری. هر حرفی داشتی، مستقیم برام بفرست به این آیدی:\n\n"
        f"📩 @gafelson\n\n"
        f"https://github.com/GafelSon/tabarskill-telegram-bot"
    )

    e_onboarding = markdownES(onboarding)

    await query.message.reply_text(
        text=header + e_onboarding,
        parse_mode="MarkdownV2",
    )
