import json
import os
import base64
import threading
from flask import Blueprint, request, abort, jsonify
from controller.src.main import main

change_config_blueprint = Blueprint("change_config", __name__)

@change_config_blueprint.route("/optima/api/coding/openaideployment", methods=["POST"])
def change_config():
    if request.method == "POST":
        #TODO namen ggf. ändern
        event = {
            "header": dict(request.headers),  
            "body": json.loads(request.get_data().decode())
        }
        basic_auth = event["header"].get("Authorization", None)
        if basic_auth:
            # The auth_header should be in the format "Basic base64encoded(username:password)"
            auth_type, auth_string = basic_auth.split(" ")

            print("auth_type", auth_type)
            print("auth_string", auth_string)

            if auth_type == "Basic":
                # Decode the base64 encoded username:password
                auth_string = base64.b64decode(auth_string).decode("utf-8")
                username, password = auth_string.split(":")

                print("username", username)
                print("Optima-FE-Username", os.environ["OPTIMA-FE-USERNAME"])
                print("password", password)
                print("Optima-FE-Password", os.environ["OPTIMA-FE-PASSWORD"])

                if username == os.environ["OPTIMA-FE-USERNAME"] \
                   and password == os.environ["OPTIMA-FE-PASSWORD"]:
                    json_deployment = event["body"]["JSON-DEPLOYMENT"]
                    text_deployment = event["body"]["TEXT-DEPLOYMENT"]
                    git_repo = event["body"]["GIT-REPO"]
                    pr_number = event["body"]["PR-NUMBER"]
                    thread = threading.Thread(target=main, args=(json_deployment, text_deployment, git_repo, pr_number))
                    thread.start()
                    return jsonify({"message": "Success"}), 200
                else:
                    print("Unauthorized")
                    return jsonify({"message": "Unauthorized"}), 401
            else:
                print("Invalid Authorization")
                return jsonify({"message": "Invalid Authorization"}), 401
    else:
        abort(400)
    
