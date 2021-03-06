# Copyright Robert Geil 2019

import parse
import database_interface as db
import tracked_item as tracked
import sys

def generate_google_home_response(data):
    try:
        intention = data['queryResult']['intent']['displayName']
        parameters = data['queryResult']['parameters']
        user = data['originalDetectIntentRequest']['payload']['user']['userId']
    except KeyError:
        print("Bad json provided by /google endpoint: {}".format(data), file=sys.stderr)
        return {'fulfillmentText': "I didn't quite understand that question"}

    if intention == 'hours':
        hall = parameters['dining_hall']
        hours = parameters['times']
        if hours == '':
            return {'fulfillmentText': get_hours(hall)}
        else:
            return {'fulfillmentText': get_specific_hours(hall, hours)}
    if intention == 'search':
        hall = None if parameters['dining_hall'] == '' else parameters['dining_hall']
        item = parameters['food']
        return {'fulfillmentText': get_queried_food_item(item, hall)}
    # All the below intentions create a user id if it hasn't been seen before
    if intention == 'list':
        return {'fulfillmentText': tracked.list_tracked_items(user, insert_on_dne=True)}
    if intention == 'add':
        item = parameters['food']
        return {'fulfillmentText': tracked.add_google_tracked_item(item, user)}
    if intention == 'remove':
        item = parameters['food']
        return {'fulfillmentText': tracked.remove_google_tracked_item(item, user)}
    if intention == 'today':
        hall = parameters.get('dining_hall')
        meal = parameters.get('times')
        if hall == '':
            hall = None
        if meal == '':
            meal = None
        return {'fulfillmentText': get_items_today(user, hall=hall, time=meal)}
    return {'fulfillmentText': "I don't understand that question"}


def generate_groupme_response(text, group_id):
    intention = parse.parse_groupme_intent(text)
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


def get_queried_food_item(item, hall):
    query = ''' SELECT dining_hall, meal, name
                FROM dining.menu 
                JOIN dining.food f ON f.food_id = menu.food_id
                WHERE day = (NOW() AT TIME ZONE 'US/Pacific')::date
                AND name = %s {};'''.format('' if hall is None else 'AND dining_hall = %s ')
    params = (item,) if hall is None else (item, hall,)

    with db.db_pool.connect() as conn:
        rs = conn.execute(query, params).fetchall()

    if len(rs) == 0:
        return "{} isn't being served in {} today".format(item, 'any dining hall' if hall is None else hall)
    results = {}
    for row in rs:
        if row[0] in results:
            results[row[0]].append(row[1])
        else:
            results[row[0]] = [row[1]]

    if hall is not None:
        return "{} is in {} at {}".format(item, hall, _format_list(results[hall]))

    allhalls = []
    for result in results:
        allhalls.append("{} at {}".format(result, _format_list(results[result])))
    return "{} is in {}".format(item, _format_list(allhalls))




def get_specific_hours(hall, meal):
    hours_query = "SELECT hour FROM dining.hours WHERE hall = %s AND meal = %s AND day = (NOW() AT TIME ZONE 'US/Pacific')::date;"
    hours = db.execute_query(hours_query, values=(hall,meal,), results=True)
    if len(hours) == 0:
        return "{} isn't open for {} today".format(hall, meal)
    return "{} is open for {} from {}".format(hall, meal, hours[0][0])


def get_hours(hall):
    hours_query = "SELECT meal, hour FROM dining.hours WHERE hall = %s AND day = (NOW() AT TIME ZONE 'US/Pacific')::date;"
    hours = db.execute_query(hours_query, values=hall, results=True)
    if len(hours) == 0:
        return '{} is closed today'.format(hall)
    response = 'The hours in {hall} today are\n{results}'.format(hall=hall,
                                                                 results=',\n'.join(i[0]+": "+i[1] for i in hours))
    return response


def get_items_today(group_id, hall=None, time=None):
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
    return _format_time_specific(m_data, hall, time)


def _format_time_specific(items_dict, hall, time):
    msg = ""
    # Nothing has been specified
    if hall is None and time is None:
        return _format_text(items_dict)
    # Only a hall has been specified
    if time is None:
        if hall in items_dict:
            allitems = []
            for item in items_dict[hall]:
                allitems.append("{} at {}".format(item, _format_list(items_dict[hall][item])))
            return "In {} today, there is {}".format(hall, _format_list(allitems))
        else:
            return "No tracked items are in {}".format(hall)
    # Only a time has been specified
    if hall is None:
        locations = []
        for hall in items_dict:
            for item in items_dict[hall]:
                if time in items_dict[hall][item]:
                    locations.append([item, hall])
        if len(locations) == 0:
            return "None of your items are being served at {}".format(time)
        return "At {}, there is {}".format(time, ",".join("{} in {}".format(i[0], i[1]) for i in locations))

    # Both a time and hall have been specified
    if hall in items_dict:
        msg = ""
        items = []
        for item in items_dict[hall]:
            if time in items_dict[hall][item]:
                items.append(item)
        if len(items) != 0:
            return "In {} at {}, there is {}".format(hall, time, _format_list(items))
        return "None of your tracked items are in {} at {}".format(hall, time)



def _format_text(items_dict):
    msg = ""
    for hall in items_dict:
        for item in (items_dict[hall]):
            msg += item + " is in " + hall + " at " + _format_list(items_dict[hall][item]) + "\n"

    if len(msg) > 0:
        msg = "Today in the dining halls:\n" + msg
    else:
        msg = "None of your selected items are in any dining hall today"
    return msg


def _format_list(items):
    if len(items) == 0:
        return ''
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return items[0] + " and " + items[1]
    return ', '.join(items[:-1]) + " and " + items[-1]


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

