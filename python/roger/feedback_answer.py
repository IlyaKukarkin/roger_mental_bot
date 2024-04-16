"""Module providing callbacks for feedback collection."""

from aiogram import types
from aiogram.types import ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import bold, text
from aiogram.utils.exceptions import MessageError

from variables import botClient
from states import Recording
from db.users import (
    get_user_by_telegram_id
)


async def feedback_answer_start(message: types.Message):
    """
    Callback handler for /supportanswer command

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    user = get_user_by_telegram_id(str(message.chat.id))

    if not user["is_admin"]:
        await botClient.send_message(
            message.chat.id,
            "Сорри, ты не админ этого бота. Не расстраивайся, ты же клиент!"
        )
        return

    await Recording.AwaitForAnAnswerToFeedback.set()
    await botClient.send_message(
        message.chat.id,
        (
            "Жду от тебя ответа на обращение. Пиши его ниже. "
            "Не забудь прикрепить реплай, на что именно отвечаем"
        )
    )


async def feedback_send_text_to_user(message: types.Message, state: FSMContext):
    """
    Adds a new user record to the DataBase table "Users"

    Parameters:
    message (TG Message): message to handle
    state (TG State): current state

    Returns:
    None
    """

    try:
        await state.update_data(AwaitForAnAnswerToFeedback=message.text)

        if isinstance(message.reply_to_message.text, type(None)):
            mes_str = message.reply_to_message.caption
        else:
            mes_str = message.reply_to_message.text

        feedback_chat_id = mes_str.partition('chat_id: ')[2].partition('.')[0]
        feedback_message_id = mes_str.partition(
            'message_id: ')[2].partition('.')[0]

        await botClient.send_message(
            int(feedback_chat_id),
            text(bold("Разработчик прислал ответ на твое обращение: \n\n")) +
            message.text,
            reply_to_message_id=int(feedback_message_id),
            parse_mode=ParseMode.MARKDOWN
        )

        await botClient.send_message(message.chat.id, "Ответ на обращение отправлен")
    except MessageError:
        await botClient.send_message(message.chat.id, "Не получилось отправить. Сделай все заново")

    await state.finish()
