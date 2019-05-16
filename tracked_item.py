# Copyright Robert Geil 2019

import database_interface as db

get_food_id_query = '''SELECT food_id FROM food WHERE name = %s;'''
add_food_id_query = '''INSERT INTO tracked_items VALUES (%s, %s);'''
delete_food_id_query = '''DELETE FROM tracked_items WHERE group_id = %s AND food_id = %s;'''
list_items_query = '''SELECT name FROM tracked_items JOIN food ON food.food_id = tracked_items.food_id WHERE group_id = %s;'''

def add_tracked_item(name, group_id):
    item_key = db.execute_query(get_food_id_query, values=name, results=True)
    if len(item_key) == 0:
        return "{} doesn't appear to be a valid food item".format(name)
    db.execute_query(add_food_id_query, values=(group_id, item_key[0][0]))
    return "Now tracking {}".format(name)


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

