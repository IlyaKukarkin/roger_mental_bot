import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# tokens
token_bot = os.getenv("TOKEN_ROGER_PROD_BOT")
#token_bot = os.getenv("TOKEN_BOT")
db_token = os.getenv("MONGODB_URI")
link_to_form = os.getenv("LINK_TO_FORM")
contenful_access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")
contenful_space_id = os.getenv("CONTENTFUL_SPACE_ID")
contentful_api_readonly_url = os.getenv("CONTENTFUL_API_READONLY_URL")
cuttly_api_key = os.getenv("CUTTLY_API_KEY")

bot = Bot(token=token_bot)
dp = Dispatcher(bot, storage=MemoryStorage())

