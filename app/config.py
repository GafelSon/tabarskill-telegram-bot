import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print(
    """
     ██████╗  █████╗ ███████╗███████╗██╗     ███████╗ ██████╗ ███╗   ██╗
    ██╔════╝ ██╔══██╗██╔════╝██╔════╝██║     ██╔════╝██╔═══██╗████╗  ██║
    ██║  ███╗███████║█████╗  █████╗  ██║     ███████╗██║   ██║██╔██╗ ██║
    ██║   ██║██╔══██║██╔══╝  ██╔══╝  ██║     ╚════██║██║   ██║██║╚██╗██║
    ╚██████╔╝██║  ██║██║     ███████╗███████╗███████║╚██████╔╝██║ ╚████║
     ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
    """
)


class Config:
    # Telegram Bot Configuration
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", None)
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN must be set in .env file")

    # Webhook Configuration
    TELEGRAM_WEBHOOK_URL = os.getenv(
        "TELEGRAM_WEBHOOK_URL", "https://api.telegram.org"
    )
    TELEGRAM_WEBHOOK_PATH = os.getenv("TELEGRAM_WEBHOOK_PATH", "/api")
