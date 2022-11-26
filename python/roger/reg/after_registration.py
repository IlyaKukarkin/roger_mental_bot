from bson import ObjectId

from config import bot, link_to_form

async def create_new_message_after_registration(telegram_id: str, name: str, form_id: ObjectId):
    await bot.send_message(int(telegram_id), 
    name + ", давай создадим твое первое сообщение для тех, у кого был плохой день. \n\nНажимай на ссылку ниже — по ней откроется небольшая форма. Помни, что твое сообщение прочитает человек, которому нужна максимальная поддержка 🙌\n\n" + link_to_form + str(form_id), disable_web_page_preview=True)
