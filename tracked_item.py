# Copyright Robert Geil 2019

import database_interface as db
import random

insert_group_id_query = '''INSERT INTO dining.groups (group_id) VALUES (%s) ON CONFLICT DO NOTHING;'''
get_food_id_query = '''SELECT f.food_id, name FROM dining.food f LEFT JOIN dining.tracked_items t ON t.food_id = f.food_id WHERE {};'''
add_food_id_query = '''INSERT INTO dining.tracked_items VALUES (%s, %s) ON CONFLICT DO NOTHING;'''
google_add_food_id_query = '''INSERT INTO dining.tracked_items (group_id, food_id) VALUES (%s, (SELECT food_id FROM food WHERE name = %s LIMIT 1));'''
delete_food_id_query = '''DELETE FROM dining.tracked_items WHERE group_id = %s AND food_id = %s;'''
list_items_query = '''SELECT name FROM dining.tracked_items JOIN dining.food ON food.food_id = tracked_items.food_id WHERE group_id = %s;'''
generate_saved_query = '''INSERT INTO dining.temporary_queries (token, group_id, food_id) VALUES (%s, %s, %s); '''

select_saved_query = '''SELECT group_id, food.food_id, name 
                        FROM dining.temporary_queries 
                        JOIN dining.food ON food.food_id = temporary_queries.food_id
                        WHERE token = %s AND time > NOW() - INTERVAL '10 minute';'''
purge_query = '''DELETE FROM dining.temporary_queries WHERE time < NOW() - INTERVAL '10 minute' RETURNING food_id;'''
drop_token_query = '''DELETE FROM dining.temporary_queries WHERE token = %s;'''

URL='saucebot.net'
chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ0123456789'


def add_tracked_item(name, group_id):
    query = get_food_id_query.format('(group_id IS NULL OR group_id != %s) AND ' + ' AND '.join('name ~* %s' for _ in name))
    item_key = db.execute_query(query, values=[group_id] + name, results=True)
    if len(item_key) == 0:
        query = get_food_id_query.format(' AND '.join('name ~* %s' for _ in name))
        item_key = db.execute_query(query, values=name, results=True)
        if len(item_key) == 0:
            return "{} doesn't appear to be a valid food item".format(' '.join(name))
        else:
            return "{} is already being tracked".format(' '.join(name))

    if len(item_key) > 1:
        return _generate_temporary_modify_urls(item_key, group_id, 'i')

    db.execute_query(add_food_id_query, values=(group_id, item_key[0][0]))
    return "Now tracking {}".format(item_key[0][1])


def add_google_tracked_item(name, group_id):
    with db.db_pool.connect() as conn:
        conn.execute(insert_group_id_query, group_id)
        id_value = conn.execute("SELECT food_id FROM dining.food WHERE name = %s", name).fetchall()
        if len(id_value) == 0:
            print("ERROR: food item {} provided by google didn't match in the database!".format(name))
            return "Something went wrong and I couldn't find that exact item"
        conn.execute("INSERT INTO dining.tracked_items (group_id, food_id) VALUES (%s, %s);", (group_id, id_value[0][0]))
        return "I'm now tracking {}".format(name)


def remove_google_tracked_item(name, group_id):
    with db.db_pool.connect() as conn:
        conn.execute(insert_group_id_query, group_id)
        id_value = conn.execute('''SELECT f.food_id FROM dining.food f 
                                JOIN dining.tracked_items t ON t.food_id = f.food_id 
                                WHERE name = %s AND t.group_id = %s;''', (name, group_id,)).fetchall()
        if len(id_value) == 0:
            return "{} isn't being tracked".format(name)
        conn.execute("DELETE FROM dining.tracked_items WHERE food_id = %s AND group_id = %s;", (id_value[0][0], group_id,))
        return "No longer tracking {}".format(name)


def remove_tracked_item(name, group_id):
    query = get_food_id_query.format('group_id = %s AND ' + ' AND '.join('name ~* %s' for _ in name))
    item_key = db.execute_query(query, values=[group_id]+name, results=True)

    if len(item_key) == 0:
        query = get_food_id_query.format(' AND '.join('name ~* %s' for _ in name))
        item_key = db.execute_query(query, values=name, results=True)
        if len(item_key) == 0:
            return "{} doesn't appear to be a valid food item".format(' '.join(name))
        else:
            return "{} isn't being tracked".format(' '.join(name))

    if len(item_key) > 1:
        return _generate_temporary_modify_urls(item_key, group_id, 'd')

    db.execute_query(delete_food_id_query, values=(group_id, item_key[0][0]))
    return "No longer tracking {}".format(item_key[0][1])


def list_tracked_items(group_id, insert_on_dne=False):
    with db.db_pool.connect() as conn:
        if insert_on_dne:
            conn.execute(insert_group_id_query, group_id)
        result_list = conn.execute(list_items_query, group_id).fetchall()
        if len(result_list) == 0:
            response = "No items are being tracked"
        else:
            response = "I'm tracking \n{}".format(",\n".join(i[0] for i in result_list))
        return response


def _generate_random_string(count):
    result = ''
    for i in range(count):
        result += random.choice(chars)
    return result


def load_token_query(token, insert):
    result = db.execute_query(select_saved_query, values=token, results=True)
    if len(result) == 0:
        return ['Unable to {} the selected item'.format('add' if insert else 'remove')]
    result = result[0]
    if insert:
        db.execute_query(add_food_id_query, values=(result[0], result[1]))
        db.execute_query(drop_token_query, values=token)
        return ['Now tracking {}'.format(result[2]), result[0]]
    else:
        db.execute_query(delete_food_id_query, values=(result[0], result[1]))
        db.execute_query(drop_token_query, values=token)
        return ['No longer tracking {}'.format(result[2]), result[0]]


def _generate_temporary_modify_urls(items, group_id, i_or_d):
    response = "I couldn't find that exact item, did you mean\n"
    for item in items[:5]:
        token = _generate_random_string(8)
        db.execute_query(generate_saved_query, values=(token, group_id, item[0]))
        response += '- {item}\n({url}/{type}?t={token})\n'.format(item=item[1], url=URL, token=token, type=i_or_d)
    return response


def purge_old_cached_queries():
    deleted = db.execute_query(purge_query, results=True)
    return 'Deleted {} cached queries from the database'.format(len(deleted))

