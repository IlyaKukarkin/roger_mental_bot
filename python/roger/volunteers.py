from database import get_database
from config import bot


async def mental_rate_strike(chat_id: int):
    collection_name = get_database()
    user = collection_name["users"].find_one(
        {"telegram_id": str(chat_id)}, {'_id': 1})
    all_rates = collection_name['mental_rate'].find(
        {"$and": [{"id_user": user["_id"]}, {"rate": {"$gt": 0}}]}, sort=[("date", -1)])
    if (len(list(all_rates.clone())) == 7):
        await ask_to_be_a_volunteer(chat_id)
    collection_name['users'].find().close()
    collection_name['mental_rate'].find().close()


async def ask_to_be_a_volunteer(chat_id: int):
    await bot.send_message(chat_id, "Ты дружишь со мной уже давно! Как насчет помочь мне с оценкой сообщений пользователей? \n\n Переходи в бота для волонтеров @JimmyVolunteerBot и нажимай /start")
    collection_name = get_database()
    collection_name['users'].find_one_and_update({"telegram_id": str(chat_id)}, {
                                                 "$set": {"is_volunteer": True}})
    collection_name['users'].find().close()