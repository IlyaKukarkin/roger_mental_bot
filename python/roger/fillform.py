"""Module providing functions for fillform interactions."""

from aiogram import types
from aiogram.types import ParseMode
from aiogram.utils.exceptions import MessageError

from variables import LINK_TO_FORM, botClient
from db.users import get_user_by_telegram_id
from common import get_options


async def fillform_command(message: types.Message):
    """
    Message handler for /fillform command

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    try:
        user = get_user_by_telegram_id(str(message.chat.id))

        await botClient.send_message(
            message.chat.id,
            get_options('fill_form') + ":\n" +
            LINK_TO_FORM + str(user['form_id']),
            disable_web_page_preview=True
        )
    except MessageError:
        await botClient.send_message(
            message.chat.id,
            (
                "Ой, кажется, что-то пошло не так 😞 \n"
                "Повтори отправку настроения через несколько минут или "
                "напиши разработчикам через команду /feedback"
            ),
            parse_mode=ParseMode.MARKDOWN
        )
