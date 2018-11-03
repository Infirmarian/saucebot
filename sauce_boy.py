from bs4 import BeautifulSoup
import requests
import json
import os
import csv
import time
from fuzzywuzzy import fuzz
import despacito


def parse_user_input(text, group_id):
    lower = text.strip(" \n\t\r").lower()
    temp = lower.find("!sauce bot")
    temp2 = lower.find("!saucebot")
    if temp != -1:
        lower = lower[temp+len("!sauce bot"):].strip(" \n\t\r")
    elif temp2 != -1:
        lower = lower[temp2+len("!saucebot"):].strip(" \n\t\r")
    else:
        return # I wasn't mentioned! :(
    if lower =="info":
        message_groupme("Hi, I'm Sauce Bot, a totally useless bot originally built "+
        "to track White Sauce Pasta at Covel. I've since grown and you can have me "+
        "check for other food items in the UCLA dining halls as well!\n" +
        "You can get my attention by saying !Sauce Bot and I can do things like "+ 
        "'!Sauce Bot list foods' to get a list of all the items I'm tracking "+
        "or '!Sauce Bot add [food item here]' to give me another item to track", group_id)
        return
    if lower.find("list") != -1:
        message_groupme(get_items_tracked(group_id), group_id)
        return
    if lower.find("track") != -1:
        item = lower[lower.find("track ")+6:]
        message_groupme(try_to_add(item, group_id), group_id)
        return 
    if lower.find("add") != -1:
        item = lower[lower.find("add ")+4:]
        message_groupme(try_to_add(item, group_id), group_id)
        return
    if lower.find("remove") != -1:
        item = lower[lower.find("remove ")+7:]
        message_groupme(try_to_remove(item, group_id), group_id)
        return
    if lower.find("today") != -1:
        message_groupme(get_daily_message(group_id), group_id)
        return
    if lower.find("play despacito") != -1:
        message_groupme(despacito.despacito, group_id)
        return
    message_groupme("Hi there, I'm just a new bot, and I don't know that command yet!", group_id)

def try_to_add(item, group_id):
    food_list = load_food_csv()
    for food in food_list:
        if food.lower() == item.lower():
            return add_food_item(food, group_id)
    suggestions = []
    for food in food_list:
        # Provides suggestions if nothing matched exactly. Using fuzzy string matching and contains
        suggestions.append((food, fuzz.ratio(item, food)+ 50 if food.lower().find(item.lower()) != -1 else 0))
    suggestions.sort(key= lambda tup: tup[1], reverse = True)
    top_5 = suggestions[:5]
    msg = ""
    for sug in top_5:
        if sug[1] > 50:
            msg += "- "+sug[0]+"\n"
    if len(msg) > 0:
        return "Sorry, I couldn't find the item you wanted to add. Did you mean one of these?\n" +msg
    return "I wasn't able to find any items close to what you asked for. I'm just a bot and I'm still gathering information, so check back later or try more accurate wording"


def load_dining_pages(scrape=False):
    if os.path.exists("stored_menu.json") and not scrape:
        with open("stored_menu.json", "r") as f:
            data = json.load(f)
        data.pop("date", None)
        return data
    dining_list = [
        ["Covel", "http://menu.dining.ucla.edu/Menus/Covel"],
        ["De Neve", "http://menu.dining.ucla.edu/Menus/DeNeve"],
        ["Bruin Plate", "http://menu.dining.ucla.edu/Menus/BruinPlate"],
        ["FEAST at Rieber", "http://menu.dining.ucla.edu/Menus/FeastAtRieber"]
    ]
    full_h = {}
    for location in dining_list:
        result = parse_page(location[1])
        for key in result:
            store_food_csv(result[key])
        full_h[location[0]] = result
        full_h["date"] = time.strftime("%Y %m %d", time.gmtime())
    with open("stored_menu.json", "w") as f:
        json.dump(full_h, f)
    full_h.pop("date", None)
    return full_h

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

def get_daily_message(group_id):
    h = load_dining_pages(False)
    to_check = load_list_to_check(group_id)
    raw = find_items(h, to_check)
    return format_text(raw)

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
    if not os.path.exists("food_dict.csv"):
        open("food_dict.csv", "w+").close()
    with open("food_dict.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            already_found_food.add(row[0])
    for food in food_list:
        already_found_food.add(food)
    with open("food_dict.csv", "w", newline='') as f:
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
    


def get_bot_id(group_id=None):
    with open("bot_list.json", "r") as f:
        data = json.load(f)
    if group_id is not None and group_id in data:
        return data[group_id]
    else:
        return data


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

def send_daily_messages():
    bot_list = get_bot_id()
    load_dining_pages(scrape=True)
    for group_id in bot_list:
        message_groupme(get_daily_message(group_id), group_id)

if __name__ == "__main__":
    send_daily_messages()
