"""This script is the RESTful web service used in Avalon"""

import argparse

from flask import Flask, jsonify
from flask_restx import Api
from flask.logging import create_logger

from avalonBG import __version__ as api_version
from avalonBG.mp3 import create_mp3

from api_utils import HTTPError
from pylib import AVALON_BLUEPRINT, DATABASE_NAMESPACE, GAMES_NAMESPACE, \
                  MP3_NAMESPACE, PLAYERS_NAMESPACE, RULES_NAMESPACE
from quests import QUESTS_BLUEPRINT, QUESTS_NAMESPACE

# from db_utils import db_connect


APP = Flask(__name__)


API = Api(
    QUESTS_BLUEPRINT,
    version=api_version,
    title="Avalon API",
    description="A simple Avalon API"
)

APP.register_blueprint(AVALON_BLUEPRINT)
APP.register_blueprint(QUESTS_BLUEPRINT)

API.add_namespace(DATABASE_NAMESPACE)
API.add_namespace(GAMES_NAMESPACE)
API.add_namespace(MP3_NAMESPACE)
API.add_namespace(QUESTS_NAMESPACE)
API.add_namespace(PLAYERS_NAMESPACE)
API.add_namespace(RULES_NAMESPACE)

# APP.before_first_request(db_connect)

LOG = create_logger(APP)


@APP.errorhandler(HTTPError)
def handle_invalid_usage(error):

    response = jsonify(error.__dict__)
    response.status_code = error.status_code

    return response


if __name__ == '__main__':

    PARSER = argparse.ArgumentParser()

    # optional arguments
    PARSER.add_argument("-host", type=str, help="app host", default="0.0.0.0")
    PARSER.add_argument("-port", type=int, help="app port", default=5000)
    PARSER.add_argument("-host_db", type=str, help="db host", default="rethinkdb")
    PARSER.add_argument("-port_db", type=int, help="db port", default=28015)

    # parse arguments
    ARGS = PARSER.parse_args()

    # HANDLER = RotatingFileHandler("foo.log", maxBytes=10000, backupCount=1)
    # HANDLER.setLevel(logging.INFO)
    # APP.logger.addHandler(HANDLER)

    #create_mp3(output_mp3_path="resources")

    # print(APP.before_first_request_funcs)

    # Start the RESTful web service used in Avalon
    APP.run(host=ARGS.host, port=ARGS.port, debug=True)
