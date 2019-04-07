# Copyright Robert Geil 2019

from flask import Flask, request, render_template
import sauce_boy

app = Flask(__name__, static_folder="static")


@app.route("/sauce", methods=["POST"])
def sauce():
    if request.json["sender_type"] != "bot":
        sauce_boy.parse_user_input(request.json["text"], group_id=request.json["group_id"])
    return "Thanks GroupMe!"


@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/register")
def register():
    return app.send_static_file("register.html")

if __name__ == "__main__":
    app.run(debug=True)