import asyncio
from config import token_bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
import json
import random
import time
import datetime
from aiogram import Bot, types
from aiogram.utils.markdown import hbold, bold, text, link
from aiogram.types import ChatType, ParseMode, ContentTypes
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton 
from states import Recording

green_button_answer=InlineKeyboardButton('🟢', callback_data='green_button_answer')
yellow_button_answer=InlineKeyboardButton('🟡', callback_data='yellow_button_answer')
orange_button_answer=InlineKeyboardButton('🟠', callback_data='orange_button_answer')
red_button_answer=InlineKeyboardButton('🔴', callback_data='red_button_answer')
kb_for_mental_poll=InlineKeyboardMarkup(row_width=4).add(green_button_answer, yellow_button_answer, orange_button_answer, red_button_answer)

ask_for_name_yes = InlineKeyboardButton('Это мое имя', callback_data='name_button_yes')
ask_for_name_no = InlineKeyboardButton('Задать другое имя', callback_data='name_button_no')
ask_for_name_kb = InlineKeyboardMarkup().add(ask_for_name_yes, ask_for_name_no)

bot = Bot(token=token_bot)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, text('Как твое настроение '+ bold('сегодня') +'?'), parse_mode=ParseMode.MARKDOWN, reply_markup=kb_for_mental_poll)

@dp.callback_query_handler(lambda c: c.data == 'green_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Ну тогда иди на хуй отсюдова! Долбаеб) green")
    return

@dp.callback_query_handler(lambda c: c.data == 'yellow_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Ну тогда иди на хуй отсюдова! Долбаеб) yellow")
    return

@dp.callback_query_handler(lambda c: c.data == 'orange_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Ну тогда иди на хуй отсюдова! Долбаеб) orange")
    return

@dp.callback_query_handler(lambda c: c.data == 'red_button_answer')
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Ну тогда иди на хуй отсюдова! Долбаеб) red")
    return

@dp.message_handler(commands=['meet'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Привет! 👋' + '\n' + '\n' + 'Я Роджер — бот для отслеживания твоего ментального состояния')
    time.sleep(1)
    await bot.send_message(message.chat.id, "Давай познакомимся с тобой поближе!")
    time.sleep(1)
    await bot.send_message(message.chat.id, "Только будь внимателен — зарегистрироваться можно только один раз 🙃")
    time.sleep(1)
    await bot.send_message(message.chat.id, "Тебя зовут " + message.from_user.first_name + "? Подтверди свое имя или введи другое", reply_markup=ask_for_name_kb)         
    await Recording.Name.set()
    return     

@dp.callback_query_handler(lambda c: c.data == 'name_button_yes', state=Recording.Name)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    user_name=callback_query.from_user.first_name
    await bot.send_message(callback_query.from_user.id, 'Приятно познакомиться, ' + user_name + '!') 
    time.sleep(1)
    await bot.send_message(callback_query.from_user.id, 'Пока все')   
    return

@dp.callback_query_handler(lambda c: c.data == 'name_button_no', state=Recording.Name)
async def process_callback_button1(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введи свое имя ниже')  
    await Recording.AwaitForAName.set()
    return

@dp.message_handler(state=Recording.AwaitForAName)
async def customer_name(message: types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    username=message.text
    if (username.isalpha()==1):
        await bot.send_message(message.chat.id, "Приятно познакомиться, " + username + "!")
    else:
        await bot.send_message(message.chat.id, "Ты ошибся со вводом. Введи свое имя еще раз")
        await Recording.AwaitForAName.set()
    return

@dp.message_handler(commands=['time'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, "test")

async def is_enabled():
    users = [71488343, 408662782]
    while True:
        for user_id in users:
            await bot.send_message(user_id, "Я отработал")
            await asyncio.sleep(10)

async def on_startup(x):
    asyncio.create_task(is_enabled())

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)