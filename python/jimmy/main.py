import os

from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from pymongo import MongoClient
import asyncio
import certifi
import contentful

from singleton import SingletonClass
from handlers.start import start_handler
from handlers.rate_good import rate_good_handler
from handlers.rate_bad import rate_bad_handler
from handlers.send_message import send_message_to_rate

# Get .env variables
token_volunteer_bot = os.getenv("TOKEN_VOLUNTEER_BOT")
db_uri = os.getenv("MONGODB_URI")
contenful_access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")
contenful_space_id = os.getenv("CONTENTFUL_SPACE_ID")
contentful_api_readonly_url = os.getenv("CONTENTFUL_API_READONLY_URL")

singleton = SingletonClass()

# Init bot
bot = Bot(token=token_volunteer_bot)
dispatcher = Dispatcher(bot, storage=MemoryStorage())

# Init database
database = MongoClient(db_uri, tlsCAFile=certifi.where())
collection_name = database["roger-bot-db"]

# Init contentful
client = contentful.Client(
    contenful_space_id,
    contenful_access_token
)

singleton.bot = bot
singleton.dispatcher = dispatcher
singleton.database = database
singleton.collection_name = collection_name
singleton.contentful = client


@dispatcher.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await start_handler(message)


@dispatcher.callback_query_handler(lambda c: c.data == 'rate_good')
async def rate_good_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await rate_good_handler(callback_query, state)


@dispatcher.callback_query_handler(lambda c: c.data == 'rate_bad')
async def rate_bad_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await rate_bad_handler(callback_query, state)


async def send_messages():
    while True:
        print('отправляю сообщения')
        await send_message_to_rate()

        print('Жду 50 минут')
        await asyncio.sleep(3000)


async def on_startup(x):
    asyncio.create_task(send_messages())

if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=True, on_startup=on_startup)
