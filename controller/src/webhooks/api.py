"""
Local server for testing purposes.
"""
from flask import Flask, request, abort
from controller.src.main import main

app = Flask(__name__)

events = []

@app.route("/optima/api/coding/webhook", methods=["POST", "GET"])
def webhook():
    global events
    if request.method == "POST":
        event = {
            "header": dict(request.headers),  
            "body": request.get_data().decode()
        }
        events.append(event)
        return "sucess", 200
    else:
        abort(400)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # Expose app on port 8080
