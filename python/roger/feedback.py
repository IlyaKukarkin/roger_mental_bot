"""Module providing functions for feedback interactions."""

from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, Message, CallbackQuery

from keyboards import feedback_keyboard, feedback_finish_keyboard
from states import Recording
from common import delete_keyboard
from variables import botClient, botDispatcher
from db.users import (
    get_all_admins,
    get_user_by_telegram_id
)


async def feedback_start(message: Message):
    """
    Message handler for /feedback command

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    await botClient.send_message(
        message.chat.id,
        (
            "Отлично! Приступаем к созданию фидбека?\n"
            "Если ты передумал отправлять фидбек, просто не нажимай на кнопку ниже"
        ),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=feedback_keyboard
    )


@botDispatcher.callback_query_handler(lambda c: c.data == 'feedback_start')
async def feedback_start_callback(callback_query: CallbackQuery):
    """
    Callback handler for /feedback -> "feedback_start"

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    await callback_query.answer("Не передавай конфиденциальные данные")

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await botClient.send_message(
        callback_query.from_user.id,
        (
            "Ты перешел в режим отправки фидбека. "
            "Ниже отправь любое сообщение (текст или фото) — "
            "и я перешлю его разработчикам"
        ),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=feedback_finish_keyboard
    )

    await Recording.AwaitForAFeedback.set()


@botDispatcher.callback_query_handler(
    lambda c: c.data == 'feedback_finish',
    state=Recording.AwaitForAFeedback
)
async def feedback_finish_def(callback_query: CallbackQuery, state: FSMContext):
    """
    Callback handler for /feedback -> "feedback_finish"

    Parameters:
    callback_query (TG Callback): callback to handle
    state (TG State): current state

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await botClient.send_message(
        callback_query.from_user.id,
        (
            "Ты вышел из режима отправки фидбека. "
            "Если захочешь вернуться и написать фидбек разработчикам, "
            "вызови команду /feedback"
        )
    )
    await state.finish()


@botDispatcher.callback_query_handler(lambda c: c.data == 'feedback_finish')
async def feedback_finish_def_without_message(callback_query: CallbackQuery):
    """
    Callback handler for /feedback -> "feedback_finish"

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)


async def feedback_get_text_from_user(message: Message, state: FSMContext):
    """
    Message handler for /feedback

    Parameters:
    message (TG Message): message to handle
    state (TG State): current state

    Returns:
    None
    """

    await state.update_data(name=message.text)

    user = get_user_by_telegram_id(str(message.chat.id))
    admins = get_all_admins()

    for admin in admins:
        await botClient.send_message(
            admin["telegram_id"],
            "Новый фидбек от пользователя " + user['telegram_username'] +
            ' из RogerMentalBot.\n\nchat_id: ' + str(message.chat.id) +
            '.\nmessage_id: ' + str(message.message_id) +
            '.\n\nТекст сообщения:\n"' + message.text + '"'
        )

    await botClient.send_message(message.chat.id, "Сообщение улетело разработчикам. Спасибо! 😍")
    await state.finish()


async def feedback_get_photo_from_user(message: Message, state: FSMContext):
    """
    Message handler for /feedback

    Parameters:
    message (TG Message): message to handle
    state (TG State): current state

    Returns:
    None
    """

    await state.update_data(name=message.caption)

    user = get_user_by_telegram_id(str(message.chat.id))
    admins = get_all_admins()

    for admin in admins:
        await botClient.send_message(
            admin['telegram_id'],
            "Новое фото от пользователя " +
            user['telegram_username'] + '. Вот оно:'
        )

        message_caption = message.caption
        if message_caption is None:
            message_caption = "Отправлено без подписи"

        await botClient.send_photo(
            admin['telegram_id'],
            photo=message.photo[-1].file_id,
            caption=(
                'chat_id: ' + str(message.chat.id) +
                '.\nmessage_id: ' + str(message.message_id) +
                '.\n\nТекст сообщения: "' + message_caption + '"'
            )
        )

    await botClient.send_message(message.chat.id, "Сообщение улетело разработчикам. Спасибо! 😍")
    await state.finish()
