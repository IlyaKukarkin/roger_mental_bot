"""Module providing functions for chatGPT interactions."""

from aiogram import types
from aiogram.dispatcher import FSMContext
import openai
from openai.error import RateLimitError
from pymongo.errors import PyMongoError

from variables import botClient, CHATGPT_TOKEN
from states import Recording
from keyboards import ask_for_rate_messages_support
from db.support_messages import (
    insert_income_support_message,
    insert_outcome_support_message,
    update_outcome_message_rate
)
from db.users import get_user_by_telegram_id
from common import delete_keyboard
from classes.chatgpt_arrays import ArrayOfChats

array_of_chats = ArrayOfChats()


async def support_message(message: types.Message):
    """
    Handler for /support command

    Parameters:
    message (TG Message): message to handle

    Returns:
    None
    """

    await botClient.send_message(
        message.chat.id,
        (
            "Ты перешел в режим диалога. Чтобы выйти из него, введи команду /stop. "
            "Оставить фидбек или пожаловаться на бота можно по команде /feedback\n\n"
            "Дисклеймер: ответы генерируются автоматически и могут быть несовершенны. "
            "Если у тебя возникли серьезные проблемы, "
            "пожалуйста, обратись к следующим организациям:\n\n"
            "1. Служба психологической поддержки: 8 (800) 333-44-34\n"
            "2. Региональные номера телефонов служба поддержки: "
            "[ссылка](https://secretmag.ru/survival/"
            "telefony-besplatnoi-psikhologicheskoi-pomoshi-v-rossii.htm)"
        ),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await botClient.send_message(message.chat.id, "Что стряслось, друг?")

    array_of_chats.add_message(
        message.chat.id,
        {
            'role': 'assistant',
            'content': """Отвечай от имени Роджера.
                Это бот, который поддерживает людей с плохим настроением"""
        }
    )

    await Recording.AwaitForAProblem.set()


async def support_callback(callback_query: types.CallbackQuery):
    """
    Handler for callback data in /support command

    Parameters:
    callback_query (TG Callback): callback to handle

    Returns:
    None
    """

    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await botClient.send_message(
        callback_query.from_user.id,
        (
            "Ты перешел в тестовый режим диалога. "
            "Чтобы выйти из него, введи команду /stop. "
            "Оставить фидбек или пожаловаться можно по команде /feedback"
        )
    )
    await botClient.send_message(callback_query.from_user.id, "Что стряслось, друг?")

    array_of_chats.add_message(
        callback_query.from_user.id,
        {
            'role': 'assistant',
            'content': (
                "Отвечай от имени Роджера. "
                "Это бот, который поддерживает людей с плохим настроением"
            )
        }
    )

    await Recording.AwaitForAProblem.set()


async def await_for_a_problem(message: types.Message, state: FSMContext):
    """
    Handler for messages in /support command

    Parameters:
    message (TG Message): message to handle
    state (TG State): current state

    Returns:
    None
    """

    await state.update_data(AwaitForAProblem=message.text)

    if message.text == "/stop":
        await state.finish()
        array_of_chats.delete_array(message.chat.id)
        await botClient.send_message(
            message.chat.id,
            "Ты вышел из режима диалога. Чтобы вернуться в него снова, вызови команду /support"
        )
        return

    if str(message.text)[0] == '/':
        await botClient.send_message(
            message.chat.id,
            (
                "Ты находишься в режиме диалога. Чтобы выйти из него, выбери команду /stop, "
                "а затем повторно вызови нужную команду"
            )
        )
        await Recording.AwaitForAProblem.set()
        return

    try:
        openai.api_key = CHATGPT_TOKEN

        id_user_db = get_user_by_telegram_id(str(message.chat.id))

        insert_income_support_message(
            id_user_db["_id"],
            message.chat.id,
            message.message_id,
            message.text
        )

        role = "user"
        mes = message.text.replace('\n', ' ')
        answer = {'role': role, 'content': mes}
        array_of_chats.add_message(message.chat.id, answer)
        completions = openai.ChatCompletion.create(
            model="gpt-4",
            messages=array_of_chats.get_chat(message.chat.id)
        )
        message_text = str(completions.choices[0].message.content).encode(
            'unicode_escape').decode('unicode_escape', 'ignore')

        id_message = await botClient.send_message(
            message.chat.id,
            message_text,
            reply_markup=ask_for_rate_messages_support
        )

        role = "assistant"
        answer = {'role': role, 'content': message_text}
        array_of_chats.add_message(message.chat.id, answer)

        insert_outcome_support_message(
            id_user_db["_id"],
            message.chat.id,
            id_message.message_id,
            id_message.text)

        await Recording.AwaitForAProblem.set()
    except RateLimitError:
        await botClient.send_message(
            message.chat.id,
            "Бот сейчас перегружен запросами 😿 Подожди 10 секунд и повтори свой вопрос"
        )
    except PyMongoError as e:
        await botClient.send_message(
            message.chat.id,
            (
                "Не получилось обработать запрос. "
                "Переформулируй его или попробуй повторить его позже. "
                "Ошибка: " + str(e)
            )
        )
    except Exception as ex:
        array_of_chats.delete_array(message.chat.id)
        await botClient.send_message(
            message.chat.id,
            "Извини, не мог бы ты повторить вопрос?"
        )

        


async def callback_after_click_on_button_support(callback_query: types.CallbackQuery, rate: bool):
    """
    Handler for a "rate" callback data in /support command

    Parameters:
    callback_query (TG Callback): callback to handle
    rate (bool): rate to write in DB

    Returns:
    None
    """

    await botClient.answer_callback_query(callback_query.id, text='Спасибо за оценку, bestie ❤️')
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)

    try:
        update_outcome_message_rate(
            callback_query.from_user.id,
            callback_query.message.message_id,
            rate
        )
    except PyMongoError as e:
        await botClient.send_message(
            callback_query.from_user.id,
            (
                "Не получилось обработать запрос. "
                "Переформулируй его или попробуй повторить его позже. "
                "Ошибка: " + str(e)
            )
        )
