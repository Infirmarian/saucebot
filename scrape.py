# Copyright Robert Geil 2019

from bs4 import BeautifulSoup
import requests
import database_interface as db
import time

dining_list = {
    "Covel":"http://menu.dining.ucla.edu/Menus/Covel/today",
    "De Neve":"http://menu.dining.ucla.edu/Menus/DeNeve/today",
    "Bruin Plate":"http://menu.dining.ucla.edu/Menus/BruinPlate/today",
    "FEAST":"http://menu.dining.ucla.edu/Menus/FeastAtRieber/today"
}

insert_menu_query = '''
INSERT INTO food (name) VALUES {}
ON CONFLICT DO NOTHING;
'''

insert_today = '''
INSERT INTO menu (dining_hall, meal, food_id) VALUES {}  ON CONFLICT DO NOTHING;
'''

insert_hours = '''
INSERT INTO hours (hall, meal, hour) VALUES {};
'''

last_scrape = 0


def daily_scrape():
    global last_scrape
    if time.time() > last_scrape + 3600:
        scrape_and_store_menu()
        scrape_and_store_hours()
        last_scrape = time.time()


def get_page_dom(url):
    r = requests.get(url)
    if r.status_code < 400 and r.text is not None:
        return r.text
    print("Error, the page {} was unable to be reached, or no data was delivered.".format(url))


def parse_hours():
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
    return hours_return


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
            return_val[name].append(food.text.strip('\t'))
    return return_val


def scrape_and_store_menu():
    food_list = set()
    menus = {}
    for hall, url in dining_list.items():
        result = parse_page(url)
        menus[hall] = result
        for _, items in result.items():
            food_list = food_list.union(items)

    items = ', '.join('(%s)' for _ in food_list)
    final_all_item_query = insert_menu_query.format(items)
    db.execute_query(final_all_item_query, values=list(food_list), results=False)

    # Add the daily menu into the database
    item_query = "('{hall}', '{meal}', (SELECT food_id FROM food WHERE name = %s LIMIT 1))"
    item_list = []
    query_list = []
    for hall, menu in menus.items():
        for meal, items in menu.items():
            for item in items:
                item_list.append(item)
                query_list.append(item_query.format(hall=hall, meal=meal))

    final_query = insert_today.format(', '.join(query_list))
    db.execute_query(final_query, values=item_list, results=False)

def scrape_and_store_hours():
    item_query = "('{hall}', '{meal}', %s)"
    query_values = []
    time_values = []
    res = parse_hours()
    for hall, values in res.items():
        # De-translation from the names that are presented on the webpage
        if hall == 'FEAST at Rieber':
            hall = 'FEAST'
        for meal, hours in values.items():
            if meal == 'Late':
                meal = 'Late Night'
            query_values.append(item_query.format(hall=hall, meal=meal))
            time_values.append(hours)

    query = insert_hours.format(', '.join(query_values))
    db.execute_query(query, values=time_values)


