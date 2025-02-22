from telegram.ext import CallbackContext

from app.database import Database


class DatabaseContext(CallbackContext):
    @property
    def db(self):
        return Database()
