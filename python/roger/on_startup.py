import datetime
from database import get_database
import asyncio
import pytz
from sendmessage import sendmes
from common import is_any_messages_sent_today

async def enable_task_to_send_mes():
    while True:
        s = datetime.datetime.now().strftime("%H")
        collection_name = get_database()
        users = collection_name["users"].aggregate([
            {
                '$match': {
                    'is_active': True
                }
            }, {
                '$addFields': {
                    'current_time': {
                        '$toDouble': {
                            '$dateToString': {
                                'date': datetime.datetime.now(pytz.utc),
                                'format': '%H'
                            }
                        }
                    }
                }
            }, {
                '$addFields': {
                    'user_time': {
                        '$toDouble': '$timezone'
                    }
                }
            }, {
                '$addFields': {
                    'current_user_time': {
                        '$add': [
                            '$user_time', '$current_time'
                        ]
                    }
                }
            }, {
                '$addFields': {
                    'result': {
                        '$lte': [
                            '$time_to_send_messages', '$current_user_time'
                        ]
                    }
                }
            }, {
                '$match': {
                    'result': True
                }
            }
        ])
        for user in users:
            already_sent = await is_any_messages_sent_today(user['_id'])
            if (not already_sent):
                await sendmes(int(user['telegram_id']))
        collection_name['users'].find().close()
        collection_name['user_messages'].find().close()
        await asyncio.sleep(45*60)