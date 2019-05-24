# Copyright Robert Geil 2019

import parse
import database_interface as db
import tracked_item as tracked
import time

def generate_user_response(text, group_id):
    intention = parse.parse_intent(text)
    todo = intention['tag']
    if todo is None:
        return
    if todo == 'hours':
        return get_hours(intention.get('value'))
    if todo == 'list':
        return tracked.list_tracked_items(group_id)
    if todo == 'add':
        return tracked.add_tracked_item(intention.get('value'), group_id)
    if todo == 'remove':
        return tracked.remove_tracked_item(intention.get('value'), group_id)
    if todo == 'today':
        return get_items_today(group_id)
    if todo == 'info':
        return get_info_description()
    if todo == 'generic':
        return intention.get('value')

    return "I don't know that command!"


def get_hours(hall):
    hours_query = "SELECT meal, hour FROM dining.hours WHERE hall = %s AND day = (NOW() AT TIME ZONE 'US/Pacific')::date;"
    hours = db.execute_query(hours_query, values=hall, results=True)
    if len(hours) == 0:
        return '{} is closed today'.format(hall)
    response = 'The hours in {hall} today are\n{results}'.format(hall=hall,
                                                                 results='\n'.join(i[0]+": "+i[1] for i in hours))
    return response


def get_items_today(group_id):
    query = """ SELECT m.dining_hall, f.name, m.meal
                FROM dining.menu m
                LEFT JOIN dining.food f ON f.food_id = m.food_id
                LEFT JOIN dining.tracked_items t ON t.food_id = m.food_id
                WHERE t.group_id = %s
                AND m.day = (NOW() AT TIME ZONE 'US/Pacific')::date;"""
    results = db.execute_query(query, values=group_id, results=True)
    m_data = {}
    for row in results:
        if row[0] in m_data:
            if row[1] in m_data[row[0]]:
                m_data[row[0]][row[1]].append(row[2])
            else:
                m_data[row[0]][row[1]] = [row[2]]
        else:
            m_data[row[0]] = {row[1]:[row[2]]}

    return _format_text(m_data)


def _format_text(items_dict):
    msg = ""
    for hall in items_dict:
        for item in (items_dict[hall]):
            msg += item + " is in " + hall + " at " + _format_times(items_dict[hall][item]) + "\n"

    if len(msg) > 0:
        msg = "Today in the dining halls:\n" + msg
    else:
        msg = "None of your selected items are in any dining hall today"
    return msg


def _format_times(times):
    if len(times) == 1:
        return times[0]
    if len(times) == 2:
        return times[0] + " and " + times[1]
    if len(times) == 3:
        return times[0] + ", " + times[1] + " and " + times[2]


def get_info_description():
    return '''Hi, I'm Saucebot, a friendly bot to track items in the UCLA dining halls! If you give me a list of items, I can track them! To add an item, simply say !saucebot add [item here], and to see all items that are being tracked, say !saucebot list. Some other things I can do are: 
    - !saucebot remove [item]
    - !saucebot hours at [dining hall]
    - !saucebot give me the menu today'''


def generate_daily_messages():
    query = '''SELECT group_id FROM dining.groups WHERE notify = TRUE'''
    groups = db.execute_query(query, results=True)
    results = []
    for group in groups:
        results.append([group[0], get_items_today(group[0])])
    return results

