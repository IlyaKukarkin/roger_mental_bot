from config import dp, bot


from datetime import datetime, timedelta
from database import get_database

async def mental_rates_strike_in_a_row(chat_id: int):
    collection_name = get_database()
    user = collection_name["users"].find_one(
            {"telegram_id": str(chat_id)}, {'_id': 1, 'id_user': 1})
    mental_rates = collection_name["mental_rate"].aggregate([
    {
        '$match': {
            'id_user': user['_id']
        }
    }, {
        '$sort': {
            'date': -1
        }
    }
])
    now = datetime.now()
    date_now = now.strftime("%d.%m.%Y")
    strike = 0
    mental_rates_list = list(mental_rates)
    for rate in mental_rates_list: 
        print (rate['date'].strftime("%d.%m.%Y"))
        print (date_now)
        if ((rate['date'].strftime("%d.%m.%Y")) == date_now and rate['rate']!=0):
            strike = strike + 1
            date_now = datetime.strptime(date_now, "%d.%m.%Y")
            date_now = date_now - timedelta(days=1)
            date_now = date_now.strftime("%d.%m.%Y")
        else:
            return strike
    
       
