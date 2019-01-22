# Copyright Robert Geil 2019
from bs4 import BeautifulSoup
import requests
import json
import os
import time
import csv

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

def load_dining_pages(scrape=False):
    if os.path.exists("stored_menu.json") and not scrape:
        with open("stored_menu.json", "r") as f:
            data = json.load(f)
        data.pop("date", None)
        return data
    dining_list = [
        ["Covel", "http://menu.dining.ucla.edu/Menus/Covel/today"],
        ["De Neve", "http://menu.dining.ucla.edu/Menus/DeNeve/today"],
        ["Bruin Plate", "http://menu.dining.ucla.edu/Menus/BruinPlate/today"],
        ["FEAST at Rieber", "http://menu.dining.ucla.edu/Menus/FeastAtRieber/today"]
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


def load_hours():
    with open("hours.json", "r") as f:
        data = json.load(f)
    return data
    