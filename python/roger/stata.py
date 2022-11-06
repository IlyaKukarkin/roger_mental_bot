from aiogram import types
from sqlite3 import Cursor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from common import delete_keyboard
from bson import ObjectId
import json
import urllib.parse
import requests
import pytz
import datetime
from linkpreview import link_preview
from common import get_pictures
from config import bot, link_to_form, cuttly_api_key
from volunteers import mental_rate_strike

from database import get_database

cart_cb = CallbackData("q", "id", "button_parameter")

async def kb_for_stata(messages: Cursor):
    kb_stata_messages = InlineKeyboardMarkup(row_width=1)
    for item in messages:
        i = InlineKeyboardButton(text=str(item['text'])[:30], callback_data=cart_cb.new(
            (str(item["_id"])), button_parameter="kb_mes"))
        kb_stata_messages.add(i)
    return kb_stata_messages

async def stata_show_mes(message: types.Message):
    collection_name = get_database()
    user = collection_name["users"].find_one(
        {"telegram_id": str(message.chat.id)}, {'_id': 1, "form_id": 1})
    if (await mental_rate_strike(message.chat.id, 'stata')) == False:
        await bot.send_message(message.chat.id, "Эта команда тебе пока недоступна. Замеряй свое настроение 7 дней — и она откроется!")
        return
    await bot.send_message(message.chat.id, "Подгружаю твои сообщения")
    messages = collection_name["messages"].find({"id_user": user["_id"]}, {
                                                "_id": 1, "text": 1, "media_link": 1, "is_approved": 1, "image_ids": 1, "is_anonymous": 1, "created_at": 1})
    length = len(list(messages.clone()))
    if (length == 0):
        await bot.send_message(message.chat.id, "У тебя нет созданных сообщений. Как насчет сделать первое?\n\n" + link_to_form + str(user['form_id']))
        return
    elif (length == 1):
        await send_stata(str(messages[0]["_id"]))
        return
    elif (length > 1):
        await bot.send_message(message.chat.id, "Выбери сообщение, по которому хочешь увидеть статистику", reply_markup=await kb_for_stata(messages))
    collection_name['users'].find().close()
    collection_name['messages'].find().close()

async def delete_from_cart_handler1(call: CallbackQuery, callback_data: dict):
    id_message = callback_data.get("id")
    await delete_keyboard(call.from_user.id, call.message.message_id)
    await send_stata(id_message)

async def send_stata(id_message: str):
    collection_name = get_database()
    message = collection_name["messages"].find_one(
        {"_id": ObjectId(id_message)})
    count_times = collection_name["user_messages"].find(
        {"id_message": message["_id"]}, {"_id": 1})

    is_approved = message["is_approved"] == True and 'true' or 'false'

    count_rates = collection_name["rate"].aggregate(
        [
            {
                '$match': {
                    'id_message': message["_id"]
                }
            }, {
                '$group': {
                    '_id': '$rate',
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
    )

    good_rates = 0
    bad_rates = 0

    for rate in count_rates:
        if (rate['_id'] == True):
            good_rates = rate['count']
        else:
            bad_rates = rate['count']

    curr_date = str(datetime.datetime.now(pytz.utc).isoformat())[:-6]

    user = collection_name["users"].find_one(
        {"_id": message["id_user"]}, {'telegram_id': 1})

    image_url = f"?show={str(len(list(count_times)))}&likes={good_rates}&dislikes={bad_rates}&approved={is_approved}&current_date={curr_date}&text={urllib.parse.quote(message['text'])}&created_date={message['created_date'].isoformat()}"

    if (message['media_link'] != ''):
        try:
            preview = link_preview(message['original_media_link'])

            if (not preview.title):
                preview.title = 'Ошибка получения заголовка ссылки'
            if (not preview.image):
                preview.image = 'https://images.ctfassets.net/n1wrmpzswxf2/5scp1TkHI7xSty5gSV2LfX/a2b733b18f51be6e2c1693fb7f85faa6/Mamba_UI__Error__Free_HTML_components_and_templates_built_with_Tailwind_CSS__2022-10-30_15-48-29.png'
        except (Exception):
            preview = json.dumps({"image": "https://images.ctfassets.net/n1wrmpzswxf2/5scp1TkHI7xSty5gSV2LfX/a2b733b18f51be6e2c1693fb7f85faa6/Mamba_UI__Error__Free_HTML_components_and_templates_built_with_Tailwind_CSS__2022-10-30_15-48-29.png",
                                  "title": 'Ошибка получения заголовка ссылки',
                                  })

        response = requests.get('http://cutt.ly/api/api.php?key=' +
                                cuttly_api_key + '&stats=' + message['media_link'])
        answer = json.loads(response.content)
        link_cliks = answer['stats']['clicks']

        image_url = image_url + \
            f"&link_clicks={link_cliks}&link={urllib.parse.quote(message['original_media_link'])}&link_image={urllib.parse.quote(preview.image)}&link_title={urllib.parse.quote(preview.title)}"

    if (len(message['image_ids']) != 0):
        image = await get_pictures(message['image_ids'][0])

        image_url = image_url + \
            f"&image={urllib.parse.quote('https://' + image)}"

    result_image_url = 'https://roger-bot.space/api/message-stats' + image_url

    await bot.send_photo(int(user["telegram_id"]), result_image_url)

    collection_name['messages'].find().close()
    collection_name['user_messages'].find().close()
    collection_name['rate'].find().close()
    collection_name['users'].find().close()
