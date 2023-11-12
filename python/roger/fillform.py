from aiogram import types
from aiogram.types import ParseMode


from config import LINK_TO_FORM, botClient
from database import get_database
from common import get_options


async def fillform_command(message: types.Message):
    try:
        collection_name = get_database()
        user = collection_name["users"].find_one(
            {"telegram_id": str(message.chat.id)}, {'id_user': 1, 'form_id': 1})
        await botClient.send_message(message.chat.id,
                                     await get_options('fill_form') + ":\n" + LINK_TO_FORM + str(user['form_id']), disable_web_page_preview=True)
        collection_name['users'].find().close()
    except (Exception):
        await botClient.send_message(message.chat.id, "Ой, кажется, что-то пошло не так 😞 \nПовтори отправку настроения через несколько минут или напиши разработчикам через команду /feedback", parse_mode=ParseMode.MARKDOWN)
