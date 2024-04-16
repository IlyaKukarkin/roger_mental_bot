"""Module providing functions for support message stata interactions."""

import json
import urllib.parse
from datetime import datetime
import requests
import pytz
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from linkpreview import link_preview
from linkpreview.exceptions import LinkPreviewException
from bson import ObjectId

from common import delete_keyboard, get_pictures
from variables import botClient, LINK_TO_FORM, CUTTLY_API_KEY
from volunteers import is_mental_rate_threashhold_reached
from db.users import get_user_by_telegram_id
from db.messages import (
    get_all_messages_by_user,
    get_message_by_id
)
from db.user_messages import get_all_messages_by_message_id
from db.rate import count_rates_for_message

cart_cb = CallbackData("q", "id", "button_parameter")


def kb_for_stata(messages: list):
    """
    Function to generate keyboard for all support messages

    Parameters:
    messages (list): list of "User messages" to display

    Returns:
    InlineKeyboardMarkup
    """

    kb_stata_messages = InlineKeyboardMarkup(row_width=1)
    for item in messages:
        i = InlineKeyboardButton(text=str(item['text'])[:30], callback_data=cart_cb.new(
            (str(item["_id"])), button_parameter="kb_mes"))
        kb_stata_messages.add(i)
    return kb_stata_messages


async def stata_show_mes(message: types.Message):
    """
    Message handler for /message command

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    user = get_user_by_telegram_id(str(message.chat.id))

    is_command_allowed = await is_mental_rate_threashhold_reached(message.chat.id, 'stata')

    if not is_command_allowed:
        await botClient.send_message(
            message.chat.id,
            "Эта команда тебе пока недоступна. Замеряй свое настроение 7 дней — и она откроется!"
        )
        return

    await botClient.send_message(message.chat.id, "Подгружаю твои сообщения")

    all_messages = get_all_messages_by_user(user["_id"])
    length = len(all_messages)

    if length == 0:
        await botClient.send_message(
            message.chat.id,
            (
                "У тебя нет созданных сообщений. Как насчет сделать первое?\n\n" +
                LINK_TO_FORM + str(user['form_id'])
            ),
            disable_web_page_preview=True
        )
    elif length == 1:
        await send_stata(all_messages[0]["_id"], message.chat.id)
    elif length > 1:
        await botClient.send_message(
            message.chat.id,
            "Выбери сообщение, по которому хочешь увидеть статистику",
            reply_markup=kb_for_stata(all_messages)
        )


async def delete_from_cart_handler1(call: CallbackQuery, callback_data: dict):
    """
    Callback handler for /message -> with "message" _id

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    id_message = ObjectId(callback_data.get("id"))
    await delete_keyboard(call.from_user.id, call.message.message_id)
    await send_stata(id_message, call.from_user.id)


async def send_stata(
    id_message: ObjectId,
    id_tg_user: int
):
    """
    Generate support message statistic and call image API

    Parameters:
    id_message (ObjectId): "_id" of message to generate statistics
    id_tg_user (int): Telegram user ID

    Returns:
    None
    """

    message = get_message_by_id(id_message)

    count_times = get_all_messages_by_message_id(message["_id"])

    is_approved = 'true' if message["is_approved"] else 'false'

    count_rates = count_rates_for_message(message["_id"])

    curr_date = str(datetime.now(pytz.utc).isoformat())[:-6]

    image_url = (
        "?show=" + str(len(count_times)) +
        "&likes=" + str(count_rates["rate_good"]) +
        "&dislikes=" + str(count_rates["rate_bad"]) +
        "&approved=" + str(is_approved) +
        "&current_date=" + curr_date +
        "&text=" + urllib.parse.quote(message['text']) +
        "&created_date=" + message['created_date'].isoformat()
    )

    if message['media_link'] != '':
        try:
            preview = link_preview(message['original_media_link'])

            if not preview.title:
                preview.title = 'Ошибка получения заголовка ссылки'
            if not preview.image:
                preview.image = (
                    "https://images.ctfassets.net/n1wrmpzswxf2/"
                    "5scp1TkHI7xSty5gSV2LfX/a2b733b18f51be6e2c1693fb7f85faa6/"
                    "Mamba_UI__Error__Free_HTML_components_and_templates_"
                    "built_with_Tailwind_CSS__2022-10-30_15-48-29.png"
                )

        except LinkPreviewException:
            preview.title = 'Ошибка получения заголовка ссылки'
            preview.image = (
                "https://images.ctfassets.net/n1wrmpzswxf2/"
                "5scp1TkHI7xSty5gSV2LfX/a2b733b18f51be6e2c1693fb7f85faa6/"
                "Mamba_UI__Error__Free_HTML_components_and_templates_"
                "built_with_Tailwind_CSS__2022-10-30_15-48-29.png"
            )

        response = requests.get('http://cutt.ly/api/api.php?key=' +
                                CUTTLY_API_KEY + '&stats=' + message['media_link'], timeout=10)
        answer = json.loads(response.content)
        link_cliks = answer['stats']['clicks']

        image_url = (
            image_url + "&link_clicks=" + str(link_cliks) +
            "&link=" + urllib.parse.quote(message['original_media_link']) +
            "&link_image=" + urllib.parse.quote(preview.image) +
            "&link_title=" + urllib.parse.quote(preview.title)
        )

    if len(message['image_ids']) != 0:
        image = await get_pictures(message['image_ids'][0])

        image_url = image_url + \
            f"&image={urllib.parse.quote('https://' + image)}"

    result_image_url = 'https://rogerbot.tech/api/message-stats' + image_url

    await botClient.send_photo(id_tg_user, result_image_url)
