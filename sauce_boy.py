from bs4 import BeautifulSoup
import requests
import json

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


