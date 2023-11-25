from aiogram import types
from aiogram.types import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from config import bot
from database import get_database, search_user_by_nickname, send_friends_request, search_user_by_tg_id, search_user_by_object_id, check_if_user_sent_request, check_if_user_got_request, find_all_friends, accept_decline_friend_request, check_if_user_has_username, change_empty_username_to_a_link
from common import delete_keyboard

from states import FriendsStates
from aiogram.dispatcher import FSMContext
from keyboards import add_button_for_friends_requests, friend_request_kb, create_back_kb


from aiogram.utils.callback_data import CallbackData

call_back_approve = CallbackData("Approve", "id", "friend")
call_back_decline = CallbackData("Decline", "id", "friend")
call_back_delete = CallbackData("Delete", "id", "friend_to_delete")


#статусы заявок в друзья: 
# 0 - создана
# 1 - принята
# 2 - отклонена

async def get_menu_for_command(chat_id: int):
    await bot.send_message(chat_id, "Выбери действие, которое хочешь выполнить", reply_markup = await add_button_for_friends_requests(*await count_friends_requests(chat_id)))

async def count_friends_requests(chat_id: int):    
    collection_name = get_database()
    user = await search_user_by_tg_id(chat_id)
    friends_requests_count = collection_name['friends'].count_documents({"to": user['_id'], 'status': 0})
    friends_count = collection_name['friends'].count_documents({"to": user['_id'], 'status': 1})
    friends_count += collection_name['friends'].count_documents({"from": user['_id'], 'status': 1})
    collection_name['friends'].find().close()
    return friends_requests_count, friends_count

async def await_for_a_friend_nickname(callback_query: types.CallbackQuery):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Введи ник своего друга в Telegram, а я проверю, знаком ли я с ним 🙃")
    await FriendsStates.AwaitForAFriendNicknameToAdd.set()

async def get_friend_nickname(message: types.Message, state: FSMContext):
    if message.text == "/stop":
        await state.finish()
        await bot.send_message(message.chat.id, "Ты вышел из режима ввода")
        return 
    
    if str(message.text)[0] == '/':
        await bot.send_message(message.chat.id, "Ты находишься в режиме ввода никнейма друга. Чтобы выйти из него, выбери команду /stop, а затем повторно вызови нужную команду")
        await FriendsStates.AwaitForAFriendNicknameToAdd.set()
        return

    if str(message.text)[0] != '@':
        message.text = "@" + message.text
    
    if message.text == '@':
        await bot.send_message(message.chat.id, "Это ник Павла Дурова? Перепроверь и введи корректный ник еще раз 🙃")
        await FriendsStates.AwaitForAFriendNicknameToAdd.set()
        return
    
    friend = await search_user_by_nickname(message.text, message.chat.id)

async def send_request_to_a_friend(message: types.Message):
    friend = await search_user_by_tg_id(message.user_shared.user_id)
#расписать логику по каждой ветке логики
    if (friend == None):
        await bot.send_message(message.chat.id, "Я не знаю такого пользователя, но буду рад познакомиться! Отправь своему другу ссылку на @RogerMentalBot и повтори отправку заявки, когда твой друг зарегистрируется 🙃")
        return

    user_request_sent = await check_if_user_sent_request(message.chat.id, friend['_id'])
    if (user_request_sent != None): 
        if (user_request_sent['status'] == 0):
            await bot.send_message(message.chat.id, "Ты уже отправлял заявку этому пользователю. Подожди, пока твой друг примет заявку 🕖")
            return
        if (user_request_sent['status'] == 1):
            await bot.send_message(message.chat.id, "Вы уже дружите 😄")
            return
        

    user_got_request = await check_if_user_got_request(message.chat.id, friend['_id'])
    if (user_got_request != None): 
        if (user_got_request['status'] == 0):
            await bot.send_message(message.chat.id, "Тебе этот друг уже отправлял заявку. Посмотри, кто уже отправил тебе заявки в друзья: /friends_requests")
            return
        if (user_got_request['status'] == 1):
            await bot.send_message(message.chat.id, "Вы уже дружите 😄")
            return
        

    await send_friends_request(message.chat.id, friend)
    if check_if_user_has_username(friend['telegram_username']) == False:
        friend["telegram_username"] = change_empty_username_to_a_link(int(friend['telegram_id']), friend['name'])
    await bot.send_message(message.chat.id, "Отправил запрос дружбы пользователю " + friend["telegram_username"] + ". Когда твой друг примет запрос в друзья, ты будешь получать информацию о его настроении")
        


# просмотр активных друзей
async def show_active_friends(callback_query: types.CallbackQuery):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    
    collection_name = get_database()
    user = await search_user_by_tg_id(callback_query.from_user.id)
    friends_list = collection_name['friends'].find({"from": user['_id'], 'status': 1}, {"_id": 0, "to": 1})
    friends_list = [x['to'] for x in friends_list]
    
    friends_list = list(friends_list)


    friends_list.extend(x['from'] for x in list(collection_name['friends'].find({"to": user['_id'], 'status': 1}, {"_id": 0, "from": 1})))
    if len(friends_list) == 0:
        await bot.send_message(callback_query.from_user.id, "У тебя пока нет друзей. Чтобы добавить первого друга, введи команду /friends и нажми кнопку Добавить нового друга")
        collection_name['friends'].find().close() 
        return
    collection_name['friends'].find().close()

    friends_id_list = [await search_user_by_object_id(x) for x in friends_list]
    for x in friends_id_list:
        if check_if_user_has_username(x['telegram_username']) == False:
            x["telegram_username"] = change_empty_username_to_a_link(int(x['telegram_id']), x['name'])

    usernames = ['😸' + ' ' + x['telegram_username'] for x in friends_id_list]
    mes = 'Список друзей, которым доступна информация о твоем настроении:\n\n'
    string = '\n'.join(usernames)
    mes+= string
    
    await bot.send_message(callback_query.from_user.id, mes, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await create_back_kb("friends_menu"))


async def show_info(callback_query: types.CallbackQuery):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    mes = """Рассказываю подробнее о режиме «Друзья»
    
Друзья — это пользователи, которым доступна информация о твоем настроении. Список друзей определяешь только ты.

Как только ты отмечаешь 🔴 или 🟠 настроение, твои друзья получают сообщение об этом —  они смогут написать и поддержать тебя
    """
    await bot.send_message(callback_query.from_user.id, mes, parse_mode=ParseMode.MARKDOWN)

    
async def watch_friends_internal_requests(user_id: int, message_id: int, keyboard_delete_need: bool):
    if (keyboard_delete_need == True):
        await delete_keyboard(user_id, message_id)
    collection_name = get_database()
    user = await search_user_by_tg_id(user_id)
    friends_list = collection_name['friends'].find({"to": user['_id'], 'status': 0}, {"_id": 0, "from": 1})
    friends_list = [x['from'] for x in friends_list]
    friends_list = list(friends_list)
    if (len(friends_list) == 0):
        await bot.send_message(user_id, "У тебя нет новых заявкок в друзья")
        collection_name['friends'].find().close() 
        return
    for x in friends_list: 
        friend_request_kb = InlineKeyboardMarkup()
        friends_obj = collection_name['users'].find_one({"_id": x}, {"_id": 0, "name": 1, "telegram_username": 1, "telegram_id": 1})
        friend_telegram_id = friends_obj["telegram_id"]
        friend_request_kb_approve = InlineKeyboardButton('✅', callback_data=call_back_approve.new(id='friend_approve', friend=friend_telegram_id))
        friend_request_kb_decline = InlineKeyboardButton('❌', callback_data=call_back_decline.new(id='friend_decline', friend=friend_telegram_id))
        friend_request_kb.add(friend_request_kb_approve, friend_request_kb_decline)
        if check_if_user_has_username(friends_obj['telegram_username']) == False:
            friends_obj["telegram_username"] = change_empty_username_to_a_link(int(friends_obj['telegram_id']), friends_obj['name'])
        await bot.send_message(user_id, f"Новый запрос в друзья от пользователя {friends_obj['telegram_username']}", reply_markup=friend_request_kb)
    collection_name['friends'].find().close()
    collection_name['user'].find().close()
    return 

async def friends_internal_request(callback_query: types.CallbackQuery, friend: str, approve: bool):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    friend_obj = await accept_decline_friend_request(callback_query.from_user.id, friend, approve)
    if check_if_user_has_username(friend_obj['telegram_username']) == False:
        friend_obj["telegram_username"] = change_empty_username_to_a_link(int(friend_obj['telegram_id']), friend_obj['name'])
    if approve == True: 
        await bot.send_message(callback_query.from_user.id, f"Теперь ты дружишь с {friend_obj['telegram_username']} 🔥. Когда твой друг отметит 🔴 или 🟠 настроение, я скажу тебе об этом")
        friend_obj = await search_user_by_tg_id(int(friend))
        user_obj = await search_user_by_tg_id(callback_query.from_user.id)
        if check_if_user_has_username(user_obj['telegram_username']) == False:
            user_obj["telegram_username"] = change_empty_username_to_a_link(int(user_obj['telegram_id']), user_obj['name'])
        await bot.send_message(friend_obj["telegram_id"], f"Теперь ты дружишь с {user_obj['telegram_username']}. Когда твой друг отметит 🔴 или 🟠 настроение, я скажу тебе об этом")               
        return
    await bot.send_message(callback_query.from_user.id, f"Ты отклонил заявку в друзья от {friend_obj['telegram_username']} 🙌")
    return
    

async def send_a_friend_message_about_bad_mood(id_user: int, color: str):
    mood_dict = {'green': "🟢", 'yellow': "🟡", 'orange': "🟠", 'red': "🔴"}
    user = await search_user_by_tg_id(id_user)
    friends = await find_all_friends(user, id_user)
    if not friends:
        return
    for friend_user_id in friends:
        friend = await search_user_by_object_id(friend_user_id)
        if check_if_user_has_username(user['telegram_username']) == False:
            user["telegram_username"] = change_empty_username_to_a_link(int(user['telegram_id']), user['name'])
        await bot.send_message(friend["telegram_id"], f"Твой друг {user['telegram_username']} отметил, что сегодня у него {mood_dict[color]} настроение. Ты можешь написать ему напрямую", parse_mode="Markdown", disable_web_page_preview=True)
    return

async def delete_friends(callback_query: types.CallbackQuery):
    await delete_keyboard(callback_query.from_user.id, callback_query.message.message_id)
    friends_list = await find_all_friends(await search_user_by_tg_id(callback_query.from_user.id), callback_query.from_user.id)
    await delete_friends_message(callback_query.from_user.id, friends_list, 0, 0)

async def delete_friends_message(id_user: int, friends_list: list, index_to_show: int, id_message: int): 
    if (len(friends_list)==0):
        await bot.send_message(id_user, "У тебя не осталось друзей 🥲", reply_markup=await create_back_kb("friends_menu"))
        return
    friends_delete_message_kb = InlineKeyboardMarkup(one_time_keyboard=True)
    mes = "😻 Твой друг: /n/n"
    friend = await search_user_by_object_id(friends_list[index_to_show])
    if (check_if_user_has_username(friend['telegram_username'])) == True: 
        mes += friend['telegram_username']
    else:
        change_empty_username_to_a_link(friend['telegram_id'], friend['name'])
    friends_button_delete = InlineKeyboardButton('😿 Удалить друга', callback_data=call_back_decline.new(id='friend_delete', friend_to_delete=friend['_id']))
    


#ебануть навигацию везде