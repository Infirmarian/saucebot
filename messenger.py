# Copyright Robert Geil 2019

import requests
import time
import database_interface as db


def message_group(msg, group_id):
    # GroupMe limits the number of characters to post at ~1000, so if we exceed 990 chars, the message
    # needs to be broken up
    i = 0
    messages = []
    while (i < len(msg)):
        messages.append(msg[i:i + 990])
        i += 990
    # Identify the id to send the query to
    bot_id = db.execute_query('SELECT bot_id FROM dining.groups WHERE group_id = %s', values=group_id, results=True)
    if len(bot_id) > 0:
        bot_id = bot_id[0][0]

    if len(messages) == 1:
        sleep_time = 0
    else:
        sleep_time = 0.5

    for message in messages:
        data = {
            "bot_id": bot_id,
            "text": message
        }
        response = requests.post("https://api.groupme.com/v3/bots/post", data=data)
        if response.status_code < 400:
            print("Bot successfully posted message!")
        else:
            print("Error, message wasn't sent")
        time.sleep(sleep_time)


