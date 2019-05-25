# Copyright Robert Geil 2019

from flask import Flask, request, render_template, send_file
import database_interface as db
import messenger
import response
import tracked_item
import scrape
import json

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/privacy')
def privacy_policy():
    return send_file('static/privacy.pdf', mimetype='application/pdf')


@app.route('/db')
def database():
    rs = db.execute_query('SELECT * FROM dining.food LIMIT 10;', results=True)
    return render_template('db_result.html', results=rs)


@app.route('/i')
def insert():
    token = request.args.get('t')
    res = tracked_item.load_token_query(token, insert=True)
    if len(res) == 1:
        return "<h1>{}</h1>".format(res[0])
    else:
        messenger.message_group(res[0], res[1])
        return "<h1>{}</h1>".format(res[0])


@app.route('/d')
def delete():
    token = request.args.get('t')
    res = tracked_item.load_token_query(token, insert=False)
    if len(res) == 1:
        return "<h1>{}</h1>".format(res[0])
    else:
        messenger.message_group(res[0], res[1])
        return "<h1>{}</h1>".format(res[0])


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
    print(request.json)
    r = response.generate_google_home_response(request.json)
    resp = app.response_class(
        response = json.dumps(r),
        status=200,
        mimetype='application/json'
    )
    return resp

@app.route('/internal/scrape/generate_new_menu_data')
def daily_scrape():
    token = request.args.get('token')
    permission = get_authorization(token)
    if permission != 'admin' and permission != 'cron':
        return 'NOT AUTHORIZED', 403
    return scrape.daily_scrape()


@app.route('/internal/db/clear_cache')
def clear_cache():
    token = request.args.get('token')
    permission = get_authorization(token)
    if permission != 'admin' and permission != 'cron':
        return 'NOT AUTHORIZED', 403
    return tracked_item.purge_old_cached_queries()


@app.route('/internal/notify/today')
def send_daily_messages():
    token = request.args.get('token')
    permission = get_authorization(token)
    if permission != 'admin' and permission != 'cron':
        return 'NOT AUTHORIZED', 403

    results = response.generate_daily_messages()
    for result in results:
        messenger.message_group(result[1], result[0])
    return 'Notified {} groups'.format(len(results))


def get_authorization(token):
    if token is None:
        return None
    with db.db_pool.connect() as conn:
        cur = conn.execute("SELECT permission FROM auth.users WHERE token = %s;", token)
        rs = cur.fetchall()
        if len(rs) == 0:
            return None
        return rs[0][0]


if __name__ == '__main__':
    app.run()
