import time
from bson import ObjectId
from aiogram.types import ParseMode
from db.users import get_user_by_id

from variables import botClient, LINK_TO_FORM


async def create_new_message_after_registration(user_id: ObjectId, telegram_id: str):
    await botClient.send_message(int(telegram_id), """Давай быстренько расскажу тебе, что я умею:\n
/chat — тут можно пообщаться со мной. Я умею давать советы и поддерживать тебя!\n
/mentalstata — тут можно посмотреть свой календарь настроений за прошедшие дни. Выясни свои самые зеленые и красные дни!\n
/fillform — написать сообщение со словами поддержки для грустных людей\n
/message — посмотреть, как часто твое сообщение показывалось пользователям и сколько людей оно порадовало\n
/support — написать разработчикам напрямую. Они рады любым жалобам и предложениям
                                 
Ты всегда сможешь вызвать меню команд по синей кнопке Меню. Она находится в левом нижнем углу экрана""",
                                 parse_mode=ParseMode.MARKDOWN)
    user = get_user_by_id(user_id)
    time.sleep(2)

    await botClient.send_message(int(telegram_id),
                                 user["name"] + ", давай создадим твое первое сообщение для тех, у кого был плохой день. \n\nНажимай на ссылку ниже — по ней откроется небольшая форма. Помни, что твое сообщение прочитает человек, которому нужна максимальная поддержка 🙌\n\n" + LINK_TO_FORM + str(user["form_id"]), disable_web_page_preview=True)
