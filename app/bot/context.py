# app.bot.context.py
from telegram.ext import CallbackContext
from app.database import Database

# Database Context Property
class DatabaseContext(CallbackContext):
    @property
    def db(self):
        return Database()
