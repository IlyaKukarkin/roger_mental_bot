import time
from bson import ObjectId
from aiogram.types import ParseMode

from variables import botClient, LINK_TO_FORM


async def create_new_message_after_registration(telegram_id: str, name: str, form_id: ObjectId):
    await botClient.send_message(int(telegram_id), """Кайф! Давай быстренько расскажу тебе, что я умею:\n
/support - тут можно пообщаться со мной. Я умею давать советы и поддерживать тебя!\n
/mentalstata — тут можно посмотреть свой календарь настроений за прошедшие дни. Выясни свои самые зеленые и красные дни!\n
/fillform — написать сообщение со словами поддержки для грустных людей\n
/stata — посмотреть, как часто твое сообщение показывалось пользователям и сколько людей оно порадовало\n
/feedback — написать разработчикам напрямую. Они рады любым жалобам и предложениям""",
                                 parse_mode=ParseMode.MARKDOWN)

    time.sleep(4)
    if name is not None:
        await botClient.send_message(int(telegram_id),
                                     name + ", давай создадим твое первое сообщение для тех, у кого был плохой день. \n\nНажимай на ссылку ниже — по ней откроется небольшая форма. Помни, что твое сообщение прочитает человек, которому нужна максимальная поддержка 🙌\n\n" + LINK_TO_FORM + str(form_id), disable_web_page_preview=True)
    else:
        await botClient.send_message(int(telegram_id),
                                     "Давай создадим твое первое сообщение для тех, у кого был плохой день. \n\nНажимай на ссылку ниже — по ней откроется небольшая форма. Помни, что твое сообщение прочитает человек, которому нужна максимальная поддержка 🙌\n\n" + LINK_TO_FORM + str(form_id), disable_web_page_preview=True)
