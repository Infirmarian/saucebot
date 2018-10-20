from bs4 import BeautifulSoup
import requests
import json
import os

def main():
    # Get Covel's page for today
    value = requests.get("http://menu.dining.ucla.edu/Menus/Covel")
    if value.status_code != 200:
        print("Error, unable to get menu")
        return
    soup = BeautifulSoup(value.text, "lxml")
    meals = soup.select(".menu-block")
    white_sauce = False
    for meal in meals:
        meal_name = meal.h3.text
        stations = meal.select(".sect-item")
        for station in stations:
            if " ".join(station.contents[0].split()) == "Exhibition Kitchen":
                for li in station.select("li"):
                    if li.span.a.text.find("Alfredo") != -1:
                        message_groupme("For {} at Covel, there will be {} served (A.K.A. WHITE SAUCE!)".format(meal_name, li.span.a.text))
                        white_sauce = True

    if not white_sauce:
        message_groupme("Sorry bois, no white sauce at Covel today :(")


def get_page_dom(url):
    r = requests.get(url)
    if r.status_code < 400 and r.text is not None:
        return r.text
    print("Error, the page {} was unable to be reached, or no data was delivered.".format(url))


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
        return_val[name] = food_list
    return return_val


def store_food_csv(food_list):
    already_found_food = set([])
    if os.path.exists("food_dict.csv"):
        with open("food_dict.csv", "r") as f:
            for line in f:
                set.add(line)
    for food in food_list:
        already_found_food.add(food)
    with open("food_dict.csv", "r") as f:
        for item in already_found_food:
            f.write(item+"\n")
    


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


parse_page("http://menu.dining.ucla.edu/Menus/Covel")

