from flask import Blueprint, request, abort
from controller.src.main import main

webhook_blueprint = Blueprint("webhook", __name__)

@webhook_blueprint.route("/optima/api/coding/webhook", methods=["POST"])
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
