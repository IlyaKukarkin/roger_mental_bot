import urllib.parse
import pytz
import datetime
from config import bot
from dateutil.relativedelta import relativedelta

from database import get_database


async def send_rate_stata(id_message: str, type: str):
    await bot.send_message(id_message, "Подгружаю статистику, немного терпения")

    collection_name = get_database()

    date_now = datetime.datetime.now(pytz.utc)
    date_now_clear = datetime.datetime(
        date_now.year, date_now.month, date_now.day, 0, 0, 0, 0, tzinfo=pytz.utc)

    if (type == 'month'):
        from_date_str = date_now_clear - relativedelta(months=1)
    elif (type == 'week2'):
        from_date_str = date_now_clear - relativedelta(days=14)
    else:
        from_date_str = date_now_clear - relativedelta(days=7)

    from_date = datetime.datetime.strptime(
        str(from_date_str), '%Y-%m-%d %H:%M:%S%z')

    user_cursor = collection_name["users"].aggregate(
        [
            {
                '$match': {
                    'telegram_id': str(id_message)
                }
            }, {
                '$lookup': {
                    'from': 'mental_rate',
                    'localField': '_id',
                    'foreignField': 'id_user',
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$gte': [
                                        '$date', from_date
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'rates'
                }
            }
        ]
    )

    user = list(user_cursor)[0]

    print(user)

    data = []
    count_rates = 0

    for i in range(0, from_date.weekday()):
        data.append(
            {"date": i, "mood": 0, "disabled": True}
        )

    for dt in daterange(from_date.date(), date_now_clear.date()):
        for index, rate in enumerate(user['rates']):
            if (rate['date'].date() == dt):
                if (rate["rate"] != 0):
                    count_rates += 1

                data.append(
                    {"date": dt.day, "mood": rate["rate"], "disabled": False}
                )
                break

            if (index == len(user['rates']) - 1):
                data.append(
                    {"date": dt.day, "mood": 0, "disabled": True}
                )

    print(data)
    print(count_rates)

    statistic = collection_name["statistic"].find_one()

    compare = 0
    compare_total_users = 0

    if (type == 'month'):
        compare_total_users = len(statistic["users_rate_month"])
        for other_user_rates in statistic["users_rate_month"]:
            if (count_rates > other_user_rates):
                compare += 1
    elif (type == 'week2'):
        compare_total_users = len(statistic["users_rate_2week"])
        for other_user_rates in statistic["users_rate_2week"]:
            if (count_rates > other_user_rates):
                compare += 1
    else:
        compare_total_users = len(statistic["users_rate_week"])
        for other_user_rates in statistic["users_rate_week"]:
            if (count_rates > other_user_rates):
                compare += 1

    title = f"с {from_date.strftime('%d.%m.%Y')} по {date_now_clear.strftime('%d.%m.%Y')}"

    image_url = f"?username={urllib.parse.quote(user['name'])}&compare_to_others={round(compare / compare_total_users * 100)}&title={urllib.parse.quote(title)}&data={data}"

    result_image_url = 'https://roger-bot.space/api/message-stats' + image_url

    await bot.send_photo(id_message, result_image_url)

    collection_name['users'].find().close()
    collection_name['statistic'].find().close()


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)
