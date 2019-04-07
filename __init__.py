# Copyright Robert Geil 2019

import sqlite3
import sys
import logging
import logging.config
import json

food_dictionary_table_query = '''
	CREATE TABLE IF NOT EXISTS menu(
	name VARCHAR(80) PRIMARY KEY,
	frequency INTEGER
	);'''

bot_list_table_query = '''
	CREATE TABLE IF NOT EXISTS bots(
	bot_id VARCHAR(30),
	group_id INTEGER
	CONSTRAINT pk PRIMARY KEY (bot_id,group_id)
	);'''

def setup():
	# SQLite Database Setup
	try:
		conn = create_connection("sauce_data.db")
		c = conn.cursor()
		c.execute(food_dictionary_table_query)
		c.execute(bot_list_table_query)
		conn.close()
	except Exception as e:
		print(e, file=sys.stderr)

	# Logging setup
	with open("logs/logging.json") as f:
		data = json.load(f)
	logging.config.dictConfig(data)
	logger = logging.getLogger(__name__)
	logger.info("Setup Completed")


def create_connection(file):
	try:
		conn = sqlite3.connect(file)
		return conn
	except Exception as e:
		print(e, file=sys.stderr)
		return None


if __name__ == "__main__":
	setup()