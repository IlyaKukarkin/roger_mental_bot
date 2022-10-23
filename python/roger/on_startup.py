import asyncio
import os
from aiogram import Bot
from keyboards import kb_for_mental_poll
from aiogram.types import ParseMode
from database import get_database

db_token = os.getenv("MONGODB_URI")
token_bot = os.getenv("TOKEN_ROGER_PROD_BOT")
bot = Bot(token=token_bot)

