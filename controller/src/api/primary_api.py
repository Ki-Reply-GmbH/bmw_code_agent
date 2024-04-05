from flask import Flask
from controller.src.api.webhook import webhook_blueprint
from controller.src.api.change_config import change_config_blueprint

app = Flask(__name__)
app.register_blueprint(webhook_blueprint)
app.register_blueprint(change_config_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)