from bs4 import BeautifulSoup
import requests
import json
import os
import csv


def main():
    dining_list = [
        "http://menu.dining.ucla.edu/Menus/Covel/yesterday"
    ]
    for location in dining_list:
        result = parse_page(location)
        for key in result:
            store_food_csv(result[key])
    
    to_check = load_list_to_check()
    print(to_check)


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
        return data.keys()  # Return all the keys of the dictionary


def parse_page(url):
    text = get_page_dom(url)
    if text is None:
        return
    soup = BeautifulSoup(text, "lxml")
    meals = soup.select(".menu-block")
    return_val = {}
    for meal in meals:
        name = meal.h3
        food_list = meal.select("a.recipelink")
        return_val[name] = []
        for food in food_list:
            return_val[name].append(food.text)
            print(food.text)
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


main()

