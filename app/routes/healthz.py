from flask import Blueprint
import os

healthz_blueprint = Blueprint('healthz', __name__)

@healthz_blueprint.route('/', methods=['GET'])
def healthz():
    return "The server is running"

@healthz_blueprint.route('/env')
def show_env():
    return {key: value for key, value in os.environ.items()}