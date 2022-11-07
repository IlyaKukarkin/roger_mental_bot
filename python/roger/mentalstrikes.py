from config import dp, bot

from database import get_database

async def mental_rates(chat_id: int):
    collection_name = get_database()
    user = collection_name["users"].find_one(
            {"telegram_id": str(chat_id)}, {'_id': 1, 'id_user': 1})
    rates = 0

    