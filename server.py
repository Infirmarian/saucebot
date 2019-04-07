# Copyright Robert Geil 2019

from flask import Flask, request
import sauce_boy
import logging.config
import json

# Setup server logging
with open("logs/logging.json") as f:
    logging.config.dictConfig(json.load(f))
logger = logging.getLogger(__name__)


app = Flask(__name__, static_folder="static")


@app.route("/sauce", methods=["POST"])
def sauce():
    if request.json["sender_type"] != "bot":
        logger.info("Received request from group {}".format(request.json["group_id"]))
        sauce_boy.parse_user_input(request.json["text"], group_id=request.json["group_id"])
    return "Thanks GroupMe!"


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/register")
def register():
    return app.send_static_file("register.html")


if __name__ == "__main__":
    logger.info("Server Startup")
    app.run(debug=True)