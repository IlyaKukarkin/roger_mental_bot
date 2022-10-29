from aiogram import types
# import requests
# import time
# import json

from singleton import Bot
# from db.messages import Messages

async def version_handler(message: types.Message):
    bot = Bot().get_bot()
    # messages = Messages()

    # all_messages = messages.get_all()

    # for message in all_messages:
    #     link = message['media_link']
    #     original_link = link

    #     if (not ('cutt' in link)):
    #         if (link != ''):
    #             key = '2eca4592ff69d5adb035f1aa32fc02f22da93'
    #             url = message['media_link']
    #             userDomain = '0'
    #             r = requests.get('http://cutt.ly/api/api.php?key={}&short={}&userDomain={}'.format(key, url, userDomain))

    #             data = json.loads(r.text)

    #             print(data)
    #             link = data['url']['shortLink']
            
    #         messages.update_message(message['_id'], link, original_link)
    #         print('Updated!')

    #         time.sleep(15)


    await bot.send_message(message.chat.id, "Версия бота Джимми: 0.4.0")
