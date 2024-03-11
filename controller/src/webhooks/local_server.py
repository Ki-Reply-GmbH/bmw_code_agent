"""
Local server for testing purposes.
"""
from flask import Flask, request, abort

app = Flask(__name__)

events = []

@app.route("/optima/api/coding/webhooks", methods=["POST", "GET"])
def webhook():
    global events
    if request.method == "POST":
        event = {
            "data": request.get_json(),  # get JSON data from request
            "headers": dict(request.headers)  # get headers from request
        }
        print(event)
        events.append(event)
        return "sucess", 200
    elif request.method == "GET":
        return events, 200
    else:
        abort(400)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
