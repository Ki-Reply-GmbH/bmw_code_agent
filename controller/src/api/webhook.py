import os
import csv
from flask import Blueprint, request, abort
from controller.src.main import main
from controller.src.webhook_handler import WebhookHandler
from controller.src.helper import add_new_entries, remove_old_entries

webhook_blueprint = Blueprint("webhook", __name__)

@webhook_blueprint.route("/optima/api/coding/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        event = {
            "header": dict(request.headers),  
            "body": request.get_data().decode()
        }

        # Extract repo name and PR number from the event
        wh = WebhookHandler(event)
        repo_name = wh.repo
        pr_number = wh.pr_number

        # Check if the event is already in the database
        db_path = os.path.join(os.path.dirname(__file__), ".db.csv")
        with open(db_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                split_row = row[0].split(";")
                if split_row[0] == repo_name and split_row[1] == pr_number:
                    return "Event arrived already", 200

        # If not, add the event to the database and call main
        remove_old_entries(db_path)
        add_new_entries(db_path, repo_name, pr_number)
        main(event)
        return "success", 200
    else:
        abort(400)