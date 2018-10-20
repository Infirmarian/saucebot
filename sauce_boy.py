from bs4 import BeautifulSoup
import requests
import json
import os
import csv


def main():
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
    to_check = load_list_to_check()
    x = find_items(full_h, to_check)
    print(format_text(x))

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


def load_list_to_check():
    if not os.path.exists("check.json"):
        with open("check.json", "w") as f:
            json.dump({}, f)
    else:
        with open("check.json", "r") as f:
            data = json.load(f)
        return list(data.keys())  # Return all the keys of the dictionary

def add_food_item(item):
    if not os.path.exists("check.json"):
        with open("check.json", "w") as f:
            json.dump({item:0}, f)
    else:
        with open("check.json", "r") as f:
            data = json.load(f)
        if item not in data:
            data[item] = 0
            with open("check.json", "w") as f:
                json.dump(data, f)

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
    


def get_bot_id():
    with open("bot_list.json", "r") as f:
        data = json.load(f)
    if "bot_id" in data:
        return data["bot_id"]
    print("Unable to load bot ID, exiting")
    return None


def message_groupme(msg, img=None):
    data = {
        "bot_id"  : get_bot_id(),
        "text"    : msg
    }
    response = requests.post("https://api.groupme.com/v3/bots/post", data=data)
    if response.status_code < 400:
        print("Bot successfully posted message!")
    else:
        print("Error, message wasn't sent")


if __name__ == '__main__':
    main()

