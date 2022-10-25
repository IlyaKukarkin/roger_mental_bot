from aiogram.utils.markdown import bold, text
from aiogram import types
from aiogram.types import ParseMode

from singleton import Bot
from db.users import Users
from utils.images import get_pictures
from utils.keyboards import ask_for_rate_messages


async def send_message(telegram_id, message):
    bot = Bot().get_bot()
    users = Users()
    message_string = ''

    if message['is_anonymous'] == True:
        message_string = text(bold("Имя: ") + "Аноним" + '\n')
    else:
        user = users.get_user_by_id(message['id_user'])
        message_string = text(bold("Имя: ") + user['name'] + '\n')

    if len(message['image_ids']) > 0:
        message_string = message_string + '\n' + text(bold('Вложения:'))
        await bot.send_message(telegram_id, message_string, parse_mode=ParseMode.MARKDOWN)
        
        message_string = ""
        media = types.MediaGroup()
        for i in message['image_ids']:
            media.attach_photo(await get_pictures(i))
        await bot.send_media_group(telegram_id, media=media)
    else:
        message_string = message_string + '\n'

    message_string = message_string + text(bold("Сообщение: ") + '\n' + message['text'] + '\n')
    message_string = message_string + '\n'

    if message['media_link']!= "":
        message_string = message_string + text(bold("Что стоит глянуть: ") + '\n' + message['media_link'])

    message = await bot.send_message(telegram_id, message_string, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=ask_for_rate_messages)

    return message.message_id