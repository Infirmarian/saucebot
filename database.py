# Copyright Robert Geil 2019

import sqlite3
import sys
import logging

def execute_query(sqlquery):
	pass

def create_connection(file):
	try:
		conn = sqlite3.connect(file)
		return conn
	except Exception as e:
		print(e, file=sys.stderr)
		logging.error("Error accessing the database: "+str(e))
		return None