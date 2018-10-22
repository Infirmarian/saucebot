from flask import Flask, request
import sauce_boy

app = Flask(__name__)

@app.route("/test")
def test():
    print("Someone visited the test page")
    return("<h1>THANK YOU FOR VISITING</h1>")

@app.route("/sauce", methods=["POST"])
def sauce():
    print("Got em!")
    sauce_boy.parse_user_input(request.json["text"])
    return "Thanks GroupMe!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)