# app.bot.context.py
from telegram.ext import CallbackContext
from app.database import Database

# Database Context Property
class DatabaseContext(CallbackContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_data['db'] = Database()

    @property
    def db(self):
        return self.bot_data['db']
