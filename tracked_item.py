# Copyright Robert Geil 2019

import database_interface as db
import random

get_food_id_query = '''SELECT food_id, name FROM food WHERE {};'''
add_food_id_query = '''INSERT INTO tracked_items VALUES (%s, %s);'''
delete_food_id_query = '''DELETE FROM tracked_items WHERE group_id = %s AND food_id = %s;'''
list_items_query = '''SELECT name FROM tracked_items JOIN food ON food.food_id = tracked_items.food_id WHERE group_id = %s;'''
generate_saved_query = '''INSERT INTO temporary_queries (token, group_id, food_id) VALUES (%s, %s, %s); '''

select_saved_query = '''SELECT group_id, food.food_id, name 
                        FROM temporary_queries 
                        JOIN food ON food.food_id = temporary_queries.food_id
                        WHERE token = %s AND time > NOW() - INTERVAL '10 minute';'''

URL='saucebot.appspot.com/i?t='
chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ0123456789'


def add_tracked_item(name, group_id):
    query = get_food_id_query.format(' AND '.join('name ~* %s' for _ in name))
    item_key = db.execute_query(query, values=name, results=True)

    if len(item_key) == 0:
        return "{} doesn't appear to be a valid food item".format(name)
    if len(item_key) > 1:
        return _generate_temporary_add_urls(item_key, group_id)

    db.execute_query(add_food_id_query, values=(group_id, item_key[0][0]))
    return "Now tracking {}".format(item_key[0][1])


def remove_tracked_item(name, group_id):
    item_key = db.execute_query(get_food_id_query, values=name, results=True)
    if len(item_key) == 0:
        return "{} doesn't appear to be a valid food item".format(name)
    db.execute_query(delete_food_id_query, values=(group_id, item_key[0][0]))
    return "No longer tracking {}".format(name)


def list_tracked_items(group_id):
    result_list = db.execute_query(list_items_query, values=group_id, results=True)
    if len(result_list) == 0:
        response = "No items are being tracked"
    else:
        response = "I'm tracking \n{}".format("\n".join(i[0] for i in result_list))
    return response


def _generate_random_string(count):
    result = ''
    for i in range(count):
        result += random.choice(chars)
    return result


def load_token_query(token):
    result = db.execute_query(select_saved_query, values=token, results=True)
    if len(result) == 0:
        return ['Unable to add the selected item']
    result = result[0]
    db.execute_query(add_food_id_query, values=(result[0], result[1]))
    return ['Now tracking {}'.format(result[2]), result[0]]


def _generate_temporary_add_urls(items, group_id):
    response = "I couldn't find that exact item, did you mean\n"
    for item in items[:5]:
        token = _generate_random_string(8)
        db.execute_query(generate_saved_query, values=(token, group_id, item[0]))
        response += '- {item} ({url}{token})\n'.format(item=item[1], url=URL, token=token)
    return response


