import json
import os
import base64
import threading
import logging
from flask import Blueprint, request, abort, jsonify
from controller.src.main import main
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
change_config_blueprint = Blueprint('change_config', __name__)


@change_config_blueprint.route('/optima/api/coding/openaideployment',
    methods=['POST'])
def change_config():
    """
    Handles the POST request to change the configuration of an OpenAI deployment.

    This endpoint expects a POST request with a JSON body and appropriate headers including basic authentication.
    The JSON body should contain keys: 'JSON-DEPLOYMENT', 'TEXT-DEPLOYMENT', 'GIT-REPO', and 'PR-NUMBER'.
    It authenticates the user using basic authentication, and if successful, it starts a new thread to process
    the deployment using the provided parameters.

    Returns:
        - JSON response with a message of "Success" and a status code of 200 if the authentication is successful and the thread starts.
        - JSON response with a message of "Unauthorized" and a status code of 401 if the authentication fails.
        - JSON response with a message of "Invalid Authorization" and a status code of 401 if the authorization header is not properly formatted.
        - Aborts with a status code of 400 if the request method is not POST.
    """
    if request.method == 'POST':
        event = {'header': dict(request.headers), 'body': json.loads(
            request.get_data().decode())}
        basic_auth = event['header'].get('Authorization', None)
        if basic_auth:
            auth_type, auth_string = basic_auth.split(' ')
            LOGGER.debug('auth_type', auth_type)
            LOGGER.debug('auth_string', auth_string)
            if auth_type == 'Basic':
                auth_string = base64.b64decode(auth_string).decode('utf-8')
                username, password = auth_string.split(':')
                LOGGER.debug('username', username)
                LOGGER.debug('Optima-FE-Username', os.environ[
                    'OPTIMA-FE-USERNAME'])
                LOGGER.debug('password', password)
                LOGGER.debug('Optima-FE-Password', os.environ[
                    'OPTIMA-FE-PASSWORD'])
                if username == os.environ['OPTIMA-FE-USERNAME'
                    ] and password == os.environ['OPTIMA-FE-PASSWORD']:
                    json_deployment = event['body']['JSON-DEPLOYMENT']
                    text_deployment = event['body']['TEXT-DEPLOYMENT']
                    git_repo = event['body']['GIT-REPO']
                    pr_number = event['body']['PR-NUMBER']
                    thread = threading.Thread(target=main, args=(
                        json_deployment, text_deployment, git_repo, pr_number))
                    thread.start()
                    return jsonify({'message': 'Success'}), 200
                else:
                    LOGGER.debug('Unauthorized')
                    return jsonify({'message': 'Unauthorized'}), 401
            else:
                LOGGER.debug('Invalid Authorization')
                return jsonify({'message': 'Invalid Authorization'}), 401
    else:
        abort(400)
