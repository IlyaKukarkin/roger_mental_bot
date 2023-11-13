from database import get_database
from variables import botClient


async def mental_rate_strike(chat_id: int, action: str):
    collection_name = get_database()
    user = collection_name["users"].find_one(
        {"telegram_id": str(chat_id)}, {'_id': 1})
    all_rates = collection_name['mental_rate'].find(
        {"$and": [{"id_user": user["_id"]}, {"rate": {"$gt": 0}}]}, sort=[("date", -1)])
    amount = len(list(all_rates.clone()))
    collection_name['users'].find().close()
    collection_name['mental_rate'].find().close()
    if (action == 'returnvolunteer'):
        if (amount >= 7):
            await update_to_be_a_volunteer(chat_id)
            return True
    if (action == 'volunteer'):
        if (amount == 7):
            await ask_to_be_a_volunteer(chat_id)
    if (action == 'stata'):
        if (amount >= 7):
            return True
        return False
    if (action == 'mantalstata'):
        if (amount >= 14):
            return True
        return False


async def how_many_days_user_with_us(chat_id: int):
    collection_name = get_database()
    user = collection_name["users"].find_one(
        {"telegram_id": str(chat_id)}, {'_id': 1})
    all_rates = collection_name['mental_rate'].find(
        {"$and": [{"id_user": user["_id"]}, {"rate": {"$gt": 0}}]}, sort=[("date", -1)])
    amount = len(list(all_rates.clone()))
    collection_name['users'].find().close()
    collection_name['mental_rate'].find().close()
    return amount


async def ask_to_be_a_volunteer(chat_id: int):
    await botClient.send_message(chat_id, "Ты дружишь со мной уже давно! Как насчет помочь мне с оценкой сообщений пользователей? \n\nПереходи в бота для волонтеров @JimmyVolunteerBot и нажимай /start")
    collection_name = get_database()
    collection_name['users'].find_one_and_update({"telegram_id": str(chat_id)}, {
                                                 "$set": {"is_volunteer": True}})
    collection_name['users'].find().close()


async def update_to_be_a_volunteer(chat_id: int):
    collection_name = get_database()
    collection_name['users'].find_one_and_update({"telegram_id": str(chat_id)}, {
                                                 "$set": {"is_volunteer": True}})
    collection_name['users'].find().close()
