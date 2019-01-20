# © Robert Geil 2019
from bs4 import BeautifulSoup
import requests
import json


def get_page_dom(url):
    r = requests.get(url)
    if r.status_code < 400 and r.text is not None:
        return r.text
    print("Error, the page {} was unable to be reached, or no data was delivered.".format(url))

def get_save_hours():
    hours_return = {}
    soup = BeautifulSoup(get_page_dom("http://menu.dining.ucla.edu/Hours/Today"), "lxml")
    halls = soup.select(".hours-table tbody tr")
    for hall in halls:
        title = hall.select(".hours-location")[0].text
        hours_return[title] = {}
        hours_open_raw = hall.select(".hours-open")
        for h in hours_open_raw:
            meal = h["class"][1]
            hours_return[title][meal] = h.span.text
    with open("hours.json", "w") as f:
        json.dump(hours_return, f)

def load_hours():
    with open("hours.json", "r") as f:
        data = json.load(f)
    return data


get_save_hours()
    