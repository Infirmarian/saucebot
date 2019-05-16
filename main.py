# Copyright Robert Geil 2019

from flask import Flask, request, render_template
import database_interface as db
import response
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/db')
def database():
    rs = db.execute_query('SELECT * FROM food LIMIT 10;', results=True)
    return render_template('db_result.html', results=rs)


@app.route('/groupme', methods=['POST'])
def group_me():
    if request.json['sender_type'] != 'bot':
        response.parse_user_input(request.json["text"], group_id=request.json["group_id"])
    return 'groupme'


@app.route('/google', methods=['POST'])
def google_home():
    return 'request received'


if __name__ == '__main__':
    app.run()
