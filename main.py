# Copyright Robert Geil 2019

from flask import Flask, request, render_template
import database_interface as db
import messenger
import response
import tracked_item
import scrape

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/db')
def database():
    rs = db.execute_query('SELECT * FROM food LIMIT 10;', results=True)
    return render_template('db_result.html', results=rs)


@app.route('/i')
def insert():
    token = request.args.get('t')
    res = tracked_item.load_token_query(token, insert=True)
    if len(res) == 1:
        return res[0]
    else:
        messenger.message_group(res[0], res[1])
        return res[0]


@app.route('/d')
def delete():
    token = request.args.get('t')
    res = tracked_item.load_token_query(token, insert=False)
    if len(res) == 0:
        return res[0]
    else:
        messenger.message_group(res[0], res[1])
        return res[0]


@app.route('/groupme', methods=['POST'])
def group_me():
    if request.json['sender_type'] != 'bot':
        message = response.generate_user_response(request.json['text'], group_id=str(request.json['group_id']))
        if message is None:
            return ''
        messenger.message_group(message, str(request.json['group_id']))
    return 'groupme'


@app.route('/google', methods=['POST'])
def google_home():
    return 'request received'


@app.route('/internal/scrape/generate_new_menu_data')
def daily_scrape():
    return scrape.daily_scrape()



if __name__ == '__main__':
    app.run()
