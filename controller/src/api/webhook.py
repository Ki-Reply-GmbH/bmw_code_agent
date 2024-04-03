from flask import Flask, request, abort
from controller.src.main import main

app = Flask(__name__)

@app.route("/optima/api/coding/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        event = {
            "header": dict(request.headers),  
            "body": request.get_data().decode()
        }
        main(event)
        return "sucess", 200
    else:
        abort(400)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
