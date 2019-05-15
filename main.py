# Copyright Robert Geil 2019

from flask import Flask, request
import database_interface as db
import message_manage
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/db')
def database():
    return str(db.execute_query('SELECT * FROM food LIMIT 10;', results=True))


@app.route('/groupme', methods=['POST'])
def group_me():
    if request.json['sender_type'] != 'bot':
        message_manage.parse_user_input(request.json["text"], group_id=request.json["group_id"])
    return 'groupme'


@app.route('/google', methods=['POST'])
def google_home():
    return 'request received'


if __name__ == '__main__':
    app.run()
