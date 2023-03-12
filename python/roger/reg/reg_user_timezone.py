from aiogram import types
from aiogram.dispatcher import FSMContext
import datetime

from states import Registration
from config import bot

#получить таймзону пользователя
async def get_user_timezone(chat_id: int):
    await bot.send_message(chat_id, "Еще мне нужно знать твой часовой пояс, чтобы присылать сообщения, когда тебе удобно \nНапиши, сколько у тебя сейчас времени в формате ЧАСЫ:МИНУТЫ")
    await Registration.AwaitForATimeZoneToSend.set()

async def customer_timezone(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    user_current_time = message.text
    try:
        s = user_current_time.split(":")
        if (s[0].isdigit() == False or s[1].isdigit() == False):
            raise Exception("Неверно введено время")
        if (int(s[0]) < 0 or int(s[0]) > 23 or int(s[1]) < 0  or int(s[1]) > 59):
            raise Exception("Неверно введено время")
    except:
        await bot.send_message(message.chat.id, "Кажется, ты ввел что-то не то 🙃 \nНапиши, сколько у тебя сейчас времени в формате ЧАСЫ:МИНУТЫ")
        await Registration.AwaitForATimeZoneToSend.set()
        return

    time_now_utc = datetime.datetime.now(datetime.timezone.utc)
    time_zone1 = int(s[0])-time_now_utc.hour
    time_zone2 = time_now_utc.hour-int(s[0])
    if (time_zone1 < 0):
        time_zone1 = time_zone1+24
    if (abs(time_zone1) <= abs(time_zone2) and time_zone1 < 10):
        time_zone = "+0" + str(abs(time_zone1))
    elif (abs(time_zone1) <= abs(time_zone2) and time_zone1 >= 10):
        time_zone = "+" + str(abs(time_zone1))
    elif (abs(time_zone1) > abs(time_zone2) and time_zone2 < 10):
        time_zone = "-0" + str(abs(time_zone2))
    else:
        time_zone = "-" + str(abs(time_zone2))
    await state.finish()
    return time_zone