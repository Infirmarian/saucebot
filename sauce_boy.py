from bs4 import BeautifulSoup
import requests
import json
import os
import csv
import time
from fuzzywuzzy import fuzz


def parse_user_input(text, group_id):
    # I wasn't mentioned! :(
    if text.lower().find("!sauce bot") == -1:
        return
    if text.lower() == "!sauce bot info":
        message_groupme("Hi, I'm Sauce Bot, a totally useless bot originally built \
        to track White Sauce Pasta at Covel. I've since grown and you can have me \
        check for other food items in the UCLA dining halls as well!\n\
        You can get my attention by saying !Sauce Bot and I can do things like\
        '!Sauce Bot list foods' to get a list of all the items I'm tracking\
        or '!Sauce Bot add [food item here]' to give me another item to track", group_id)
        return
    if text.find("list") != -1:
        message_groupme(get_items_tracked(group_id), group_id)
        return
    if text.find("track") != -1:
        item = text[text.find("track ")+6:]
        message_groupme(try_to_add(item, group_id), group_id)
        return 
    if text.find("add") != -1:
        item = text[text.find("add ")+4:]
        message_groupme(try_to_add(item, group_id), group_id)
        return
    message_groupme("Hi there, I'm just a new bot, and I don't know that command yet!", group_id)

def try_to_add(item, group_id):
    food_list = load_food_csv()
    for food in food_list:
        if food.lower() == item.lower():
            return add_food_item(item, group_id)
    suggestions = []
    for food in food_list:
        suggestions.append((food, fuzz.ratio(item, food)))
    suggestions.sort(key= lambda tup: tup[1], reverse = True)
    top_5 = suggestions[:5]
    msg = ""
    for sug in top_5:
        if sug[1] > 50:
            msg += "- "+sug[0]+"\n"
    if len(msg) > 0:
        return "Sorry, I couldn't find the item you wanted to add. Did you mean one of these?\n" +msg
    return "I wasn't able to find any items close to what you asked for. I'm just a bot and I'm still gathering information, so check back later or try more accurate wording"


def load_dining_pages():
    dining_list = [
        ["Covel", "http://menu.dining.ucla.edu/Menus/Covel"],
        ["De Neve", "http://menu.dining.ucla.edu/Menus/DeNeve"],
        ["Bruin Plate", "http://menu.dining.ucla.edu/Menus/BruinPlate"]
    ]
    full_h = {}
    for location in dining_list:
        result = parse_page(location[1])
        for key in result:
            store_food_csv(result[key])
        full_h[location[0]] = result
        full_h["date"] = time.strftime(time.time(), "%Y %m %d")
    with open("stored_menu.json", "w") as f:
        json.dump(full_h, f)


def get_items_tracked(group_id):
    l = load_list_to_check(group_id)
    msg = "I'm currently tracking "
    if len(l) == 0:
        return "I'm not tracking any items! To add an item, say\n!Sauce Bot add [insert item here]"
    if len(l) == 1:
        return msg + l[0]
    if len(l) == 2:
        return msg + l[0] +" and "+l[1]
    if len(l) > 2:
        for i in range(len(l)-1):
            msg += l[i]+", "
        msg += "and "+l[-1]
    return msg


def format_text(items_dict):
    msg = ""
    for item in items_dict:
        for hall in (items_dict[item]):
            msg += item+" is in "+hall+" at "+format_times(items_dict[item][hall])+"\n"

    if len(msg) > 0:
        msg = "Today in the dining halls:\n"+msg
    else:
        msg = "Sorry! None of your selected items are in any dining hall today!"
    return msg

def format_times(times):
    if len(times)==1:
        return times[0]
    if len(times)==2:
        return times[0]+" and "+times[1]
    if len(times) == 3:
        return times[0] + ", "+times[1]+" and "+times[2] 

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


def get_page_dom(url):
    r = requests.get(url)
    if r.status_code < 400 and r.text is not None:
        return r.text
    print("Error, the page {} was unable to be reached, or no data was delivered.".format(url))


def load_list_to_check(group_id):
    if not os.path.exists("check.json"):
        with open("check.json", "w") as f:
            json.dump({group_id:{}}, f)
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
            json.dump({group_id:{item:0}}, f)
        return "Added {} to the list of items to check".format(item)
    else:
        with open("check.json", "r") as f:
            data = json.load(f)
        if group_id not in data:
            data[group_id] = {item:0}
        if item not in data[group_id]:
            data[item] = 0
        else:
            return "{} was already being tracked!".format(item)
        with open("check.json", "w") as f:
            json.dump(data, f)
        return "Added {} to the list of items to check".format(item)

# A functionality to remove 
def remove_food_item(item):
    if not os.path.exists("check.json"):
        with open("check.json", "w") as f:
            json.dump({}, f)
        return 0
    with open("check.json", "r") as f:
        data = json.load(f)
    existing = data.pop(item, None)
    if existing is not None:
        with open("check.json", "w") as f:
            json.dump(data, f)

def parse_page(url):
    text = get_page_dom(url)
    if text is None:
        return
    soup = BeautifulSoup(text, "lxml")
    meals = soup.select(".menu-block")
    return_val = {}
    for meal in meals:
        name = meal.h3.text
        food_list = meal.select("a.recipelink")
        return_val[name] = []
        for food in food_list:
            return_val[name].append(food.text)
    return return_val


def store_food_csv(food_list):
    already_found_food = set([])
    if os.path.exists("food_dict.csv"):
        with open("food_dict.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                already_found_food.add(row[0])
    for food in food_list:
        already_found_food.add(food)
    with open("food_dict.csv", "w") as f:
        writer = csv.writer(f)
        for item in already_found_food:
            writer.writerow([item])

def load_food_csv():
    f_list = []
    if os.path.exists("food_dict.csv"):
        with open("food_dict.csv", "r") as f:
            reader = csv.reader(f)
            for line in reader:
                f_list.append(line[0])
    return f_list
    


def get_bot_id(group_id):
    with open("bot_list.json", "r") as f:
        data = json.load(f)
    if group_id in data:
        return data[group_id]
    print("Unable to load bot ID, exiting")
    return None


def message_groupme(msg, group_id, img=None):
    data = {
        "bot_id"  : get_bot_id(group_id),
        "text"    : msg
    }
    response = requests.post("https://api.groupme.com/v3/bots/post", data=data)
    if response.status_code < 400:
        print("Bot successfully posted message!")
    else:
        print("Error, message wasn't sent")



