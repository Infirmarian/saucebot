# Copyright Robert Geil 2019
from bs4 import BeautifulSoup
import requests
import json
import os
import csv
import time
from fuzzywuzzy import fuzz
import despacito
import parse
import scrape
import database_interface as db
import tracked_item as tracked


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

    if todo == 'unknown':
        return "I don't know that command!"


def get_hours(hall):
    hours_query = "SELECT meal, hour FROM hours WHERE hall = %s AND day = (NOW() AT TIME ZONE 'US/Pacific')::date;"
    hours = db.execute_query(hours_query, values=hall, results=True)
    if len(hours) == 0:
        return '{} is closed today'.format(hall)
    response = 'The hours in {hall} today are\n{results}'.format(hall=hall,
                                                                results='\n'.join(i[0]+": "+i[1] for i in hours))
    return response


def try_to_add(item, group_id):
    food_list = load_food_csv()
    for food in food_list:
        if food.lower() == item.lower():
            return add_food_item(food, group_id)
    suggestions = []
    for food in food_list:
        # Provides suggestions if nothing matched exactly. Using fuzzy string matching and contains
        suggestions.append((food, fuzz.ratio(item, food) + 50 if food.lower().find(item.lower()) != -1 else 0))
    suggestions.sort(key=lambda tup: tup[1], reverse=True)
    top_5 = suggestions[:5]
    msg = ""
    for sug in top_5:
        if sug[1] > 50:
            msg += "- " + sug[0] + "\n"
    if len(msg) > 0:
        return "Sorry, I couldn't find the item you wanted to add. Did you mean one of these?\n" + msg
    return "I wasn't able to find any items close to what you asked for. Please try more accurate wording"


def try_to_remove(item, group_id):
    items_tracked = load_list_to_check(group_id)
    for food in items_tracked:
        if food.lower() == item.lower():
            return remove_food_item(food, group_id)

    suggestion = ""
    ratio = 0
    for food in items_tracked:
        r = fuzz.ratio(food, item)
        if r > ratio:
            ratio = r
            suggestion = food
    if suggestion == "":
        return remove_food_item(item, group_id)
    return "I couldn't find that specific food item, did you mean {}".format(suggestion)


def get_items_tracked(group_id):
    l = load_list_to_check(group_id)
    msg = "I'm currently tracking\n"
    if len(l) == 0:
        return "I'm not tracking any items! To add an item, say\n!Sauce Bot add [insert item here]"
    for item in l:
        msg += "\n-" + item + "\n"
    return msg


def format_text(items_dict):
    msg = ""
    for item in items_dict:
        for hall in (items_dict[item]):
            msg += item + " is in " + hall + " at " + format_times(items_dict[item][hall]) + "\n"

    if len(msg) > 0:
        msg = "Today in the dining halls:\n" + msg
    else:
        msg = "Sorry! None of your selected items are in any dining hall today!"
    return msg


def format_times(times):
    if len(times) == 1:
        return times[0]
    if len(times) == 2:
        return times[0] + " and " + times[1]
    if len(times) == 3:
        return times[0] + ", " + times[1] + " and " + times[2]


def find_items(full_menu, to_check):
    locations = {}
    for food in to_check:
        locations[food] = {}
        for hall in full_menu:
            for meal in full_menu[hall]:
                if food in full_menu[hall][meal]:
                    if hall in locations[food]:
                        locations[food][hall].append(meal)
                    else:
                        locations[food][hall] = [meal]
    return locations


def get_daily_message(group_id):
    h = scrape.load_dining_pages(False)
    to_check = load_list_to_check(group_id)
    raw = find_items(h, to_check)
    return format_text(raw)


def load_list_to_check(group_id):
    if not os.path.exists("check.json"):
        with open("check.json", "w") as f:
            json.dump({group_id: {}}, f)
        return []
    else:
        with open("check.json", "r") as f:
            data = json.load(f)
        # Add group to check.json
        if group_id not in data:
            data[group_id] = {}
            with open("check.json", "w") as f:
                json.dump(data, f)
        return list(data[group_id].keys())  # Return all the keys of the dictionary


def add_food_item(item, group_id):
    if not os.path.exists("check.json"):
        with open("check.json", "w") as f:
            json.dump({group_id: {item: 0}}, f)
        return "Added {} to the list of items to check".format(item)
    else:
        with open("check.json", "r") as f:
            data = json.load(f)
        if group_id not in data:
            data[group_id] = {item: 0}
        elif item not in data[group_id]:
            data[group_id][item] = 0
        else:
            return "{} was already being tracked!".format(item)
        with open("check.json", "w") as f:
            json.dump(data, f)
        return "Added {} to the list of items to check".format(item)


# A functionality to remove
def remove_food_item(item, group_id):
    if not os.path.exists("check.json"):
        with open("check.json", "w") as f:
            json.dump({}, f)
        return "Looks like you weren't tracking any items, so there was nothing for me to remove!"
    with open("check.json", "r") as f:
        data = json.load(f)
    existing = data[group_id].pop(item, None)
    if existing is not None:
        with open("check.json", "w") as f:
            json.dump(data, f)
        return "Removed {} from tracked food items".format(item)
    else:
        return "Looks like that item was not being tracked in the first place"


def load_food_csv():
    f_list = []
    if os.path.exists("food_dict.csv"):
        with open("food_dict.csv", "r") as f:
            reader = csv.reader(f)
            for line in reader:
                f_list.append(line[0])
    return f_list


def get_bot_id(group_id=None):
    with open("bot_list.json", "r") as f:
        data = json.load(f)
    if group_id is not None and group_id in data:
        return data[group_id]
    else:
        return data


if __name__ == "__main__":
    pass #send_daily_messages()
