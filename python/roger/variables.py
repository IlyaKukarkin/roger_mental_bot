import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# ENV variables
ROGER_TOKEN_BOT = os.getenv("ROGER_TOKEN_BOT")
MONGODB_URI = os.getenv("MONGODB_URI")
LINK_TO_FORM = os.getenv("LINK_TO_FORM")
CONTENTFUL_ACCESS_TOKEN = os.getenv("CONTENTFUL_ACCESS_TOKEN")
CONTENTFUL_SPACE_ID = os.getenv("CONTENTFUL_SPACE_ID")
CONTENTFUL_API_READONLY_URL = os.getenv("CONTENTFUL_API_READONLY_URL")
CUTTLY_API_KEY = os.getenv("CUTTLY_API_KEY")
ROGER_GITHUB_RESTART_TOKEN = os.getenv("ROGER_GITHUB_RESTART_TOKEN")
CHATGPT_TOKEN = os.getenv("CHATGPT_TOKEN")


# Telegram bot creation
botClient = Bot(token=ROGER_TOKEN_BOT)

# Dispatcher for telegram Bot
botDispatcher = Dispatcher(botClient, storage=MemoryStorage())
