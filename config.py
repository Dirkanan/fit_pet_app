import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_TOKEN_ERROR_MSG = "BOT_TOKEN не найден в переменных окружениях"

if not BOT_TOKEN:
    raise ValueError(BOT_TOKEN_ERROR_MSG)
