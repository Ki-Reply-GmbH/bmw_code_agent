import json
import os
from flask import Flask, request, abort
from controller.src.main import main

app = Flask(__name__)

@app.route("/optima/api/coding/openaideployment", methods=["POST"])
def change_config():
    if request.method == "POST":
        #TODO namen ggf. ändern
        event = {
            "header": dict(request.headers),  
            "body": json.loads(request.get_data().decode())
        }
        basic_auth = event["header"].get("Authorization", None)
        if basic_auth:
            # The auth_header should be in the format 'Basic base64encoded(username:password)'
            auth_type, auth_string = basic_auth.split(' ')
            if auth_type == 'Basic':
                # Decode the base64 encoded username:password
                auth_string = basic_auth.b64decode(auth_string).decode('utf-8')
                username, password = auth_string.split(':')
                if username == os.environ["OPTIMA-FE-USERNAME"] \
                   and password == os.environ["OPTIMA-FE-PASSWORD"]:
                    # Ändert die env-Variables für jeden SW-User, der den Kubernetes Pod
                    # nutzt. Sollte geändert werden, wenn das Projekt über PoC hinausgeht.
                    os.envion["JSON-DEPLOYMENT"] = event["body"]["JSON-DEPLOYMENT"]
                    os.envion["TEXT-DEPLOYMENT"] = event["body"]["TEXT-DEPLOYMENT"]
                    return "sucess", 200
                else:
                    return "Unauthorized", 401
    else:
        abort(400)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
