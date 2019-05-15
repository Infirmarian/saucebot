# Copyright Robert Geil 2019

import sqlite3
import sys
import logging
import logging.config
import json

food_dictionary_table = '''
	CREATE TABLE IF NOT EXISTS menu(
	name VARCHAR(80) UNIQUE,
	frequency INTEGER DEFAULT 0,
	id INTEGER PRIMARY KEY
	);'''

bot_list_table = '''
	CREATE TABLE IF NOT EXISTS bots(
	bot_id VARCHAR(30),
	group_id INTEGER,
	send_message INTEGER DEFAULT 1,
	CONSTRAINT pk PRIMARY KEY (bot_id,group_id)
	);'''

dining_daily_data = '''
	CREATE TABLE IF NOT EXISTS daily_data(
	food_id INTEGER,
	time_id INTEGER,
	hall_id INTEGER,
	date TIMESTAMP,
	FOREIGN KEY(hall_id) REFERENCES halls(id),
	FOREIGN KEY(food_id) REFERENCES menu(id),
	FOREIGN KEY(time_id) REFERENCES times(id)
	);
'''
dining_halls = '''
	CREATE TABLE IF NOT EXISTS halls(
	name VARCHAR(25) UNIQUE,
	id INTEGER PRIMARY KEY
	);
'''

dining_times = '''
	CREATE TABLE IF NOT EXISTS times(
	name VARCHAR(10) UNIQUE,
	id INTEGER PRIMARY KEY
	);
'''

dining_hours = '''
	CREATE TABLE IF NOT EXISTS hours(
	hall INTEGER UNIQUE,
	meal_period INTEGER,
	time_slot VARCHAR(12),
	FOREIGN KEY(meal_period) REFERENCES times(id)
	);
'''

def setup():
	# SQLite Database Setup
	try:
		conn = create_connection("sauce_data.db")
		c = conn.cursor()
		c.execute(food_dictionary_table)
		c.execute(bot_list_table)
		c.execute(dining_halls)
		c.execute(dining_times)
		c.execute(dining_daily_data)
		c.execute(dining_hours)
		conn.close()
	except Exception as e:
		print(e, file=sys.stderr)

	# Logging setup
	with open("logs/logging.json") as f:
		data = json.load(f)
	logging.config.dictConfig(data)
	logger = logging.getLogger(__name__)
	logger.info("__init.py__ Completed Setup")


def create_connection(file):
	try:
		conn = sqlite3.connect(file)
		return conn
	except Exception as e:
		print(e, file=sys.stderr)
		return None


if __name__ == "__main__":
	setup()