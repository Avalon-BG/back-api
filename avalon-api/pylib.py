"""This functions are used is the RESTful web service of Avalon"""

from flask import Blueprint, jsonify, make_response, request, send_file
from flask_cors import CORS
from flask_restx import fields, marshal_with, Namespace, Resource

from avalonBG import __version__ as api_version
from avalonBG.db_utils import db_connect, db_get_game, db_get_table, restart_db
from avalonBG.exception import AvalonBGError
from avalonBG.games import game_put, game_guess_merlin
from avalonBG.mp3 import get_mp3_roles_path
from avalonBG.rules import get_rules

from api_utils import HTTPError

# pylint: disable=R0201


AVALON_BLUEPRINT = Blueprint("avalon", __name__)
CORS(AVALON_BLUEPRINT)

AVALON_BLUEPRINT.before_request(db_connect)

DATABASE_NAMESPACE = Namespace("database", description="Database operations", path="/")
GAMES_NAMESPACE = Namespace("games", description="Games operations", path="/games")
MP3_NAMESPACE = Namespace("mp3", description="Mp3 operations", path="/games/<string:game_id>")
PLAYERS_NAMESPACE = Namespace("players", description="Players operations", path="/")
RULES_NAMESPACE = Namespace("rules", description="Rules operations", path="/")

NEWGAME_MODEL = GAMES_NAMESPACE.model(
    "NewGame",
    {
        "names": fields.List(
            fields.String(),
            example=["Romain", "Mathieu", "Chacha", "Thomas", "Elsa", "Flo", "Eglantine", "Jordan"],
            min_items=5,
            max_items=10
        ),
        "roles": fields.List(
            fields.String(),
            example=["oberon", "morgan", "mordred", "perceval"],
            min_items=0,
            max_items=4
        )
    }
)


PLAYER_MODEL = GAMES_NAMESPACE.model(
    "Player",
    {
        "assassin": fields.Boolean(
            required=False,
            description="This player is the assassin or not",
            help="Assassin guess merlin"
        ),
        "avatar_index": fields.Integer(
            required=True,
            description="Index of the avatar",
            example=1
        ),
        "id": fields.String(
            required=True,
            description="Id of the player",
            example="94ee4546-9358-4a68-a155-01876a7c583f"
        ),
        "name": fields.String(
            required=True,
            description="Name of the player",
            example="Romain"
        ),
        "role": fields.String(
            required=True,
            description="Role of the player",
            example="mordred"
        ),
        "team": fields.String(
            required=True,
            description="Team of the player",
            help="blue or red",
            example="blue"
        )
    }
)


QUEST_MODEL = GAMES_NAMESPACE.model(
    "Quest",
    {
        "id": fields.String(
            required=True,
            description="Id of the quest",
            example="856307af-2784-4c51-90d3-d7d6fda10cfa"
        ),
        "nb_players_to_send": fields.Integer(
            required=True,
            description="Number of the players to send in quest",
            example=2,
            min_items=2,
            max_items=5
        ),
        "nb_votes_to_fail": fields.Integer(
            required=True,
            description="Number of the votes to fail the quest",
            example=1,
            min_items=1,
            max_items=2
        ),
    }
)

GAME_MODEL = GAMES_NAMESPACE.model(
    "Game",
    {
        "current_id_player": fields.String(
            required=True,
            description="Id of the current player",
            example="9ef88384-fdf0-41e9-8525-6783d4b95e65"
        ),
        "current_quest": fields.Integer(
            required=True,
            description="Number of the current quest",
            example=0,
            min_items=0,
            max_items=4
        ),
        "id": fields.String(
            required=True,
            description="Id of the game",
            example="d7cf9c96-ed57-40e3-b1f3-3770f303cd45"
        ),
        "nb_quest_unsend": fields.Integer(
            required=True,
            description="Number of the quest unsend",
            example=0,
            min_items=0,
            max_items=4
        ),
        "players": fields.List(
            fields.Nested(PLAYER_MODEL),
            required=True,
            min_items=5,
            max_items=10
        ),
        "quests": fields.List(
            fields.Nested(QUEST_MODEL),
            required=True,
            min_items=5,
            max_items=5
        )
    }

)


# from flask_httpauth import HTTPBasicAuth
# from werkzeug.security import generate_password_hash, check_password_hash

# AUTH = HTTPBasicAuth()

# USERS = {
#     "mathieu": generate_password_hash("lebeaugosse"),
#     "romain": generate_password_hash("lala")
# }


# @AUTH.verify_password
# def verify_password(username, password):
#     if username in USERS:
#         return check_password_hash(USERS.get(username), password)
#     return False


# @AVALON_BLUEPRINT.route('/')
# @AUTH.login_required
# def index():
#     return "Hello, %s!" % AUTH.username()



@DATABASE_NAMESPACE.route("/restart_db")
class Database(Resource):
    @DATABASE_NAMESPACE.doc(
        responses={
            204: "OK",
            400: "Invalid Argument"
        },
        body=[
            fields.String(
                required=True,
                description="Table to restart ('games', 'players', 'quests' or 'users')",
                example="games"
            )
        ],
    )
    def put(self):
        """Restart the database"""
        try:
            response_msg = restart_db(payload_tables=request.json)
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return make_response(response_msg, 204)


@RULES_NAMESPACE.route("/rules")
class Rules(Resource):
    @RULES_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        }
    )
    def get(self):
        """Fetch the rules"""
        try:
            rules = get_rules()
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(rules)


@PLAYERS_NAMESPACE.route("/players")
class Players(Resource):
    @PLAYERS_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        }
    )
    def get(self):
        """Fetch the players"""
        try:
            table_players = db_get_table(table_name="players")
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(table_players)


@MP3_NAMESPACE.route("/mp3")
class Mp3(Resource):
    @MP3_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        }
    )
    def get(self, game_id):
        """Fetch mp3 file depending on roles in the game <game_id>"""
        try:
            mp3_roles_path = get_mp3_roles_path(game_id=game_id)
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return send_file(mp3_roles_path, attachment_filename="roles.mp3", mimetype="audio/mpeg")


@GAMES_NAMESPACE.route("/<string:game_id>/guess_merlin")
class GuessMerlin(Resource):
    @GAMES_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        }
    )
    def post(self, game_id):
        """Assassin try to guess merlin"""
        try:
            updated_game = game_guess_merlin(game_id=game_id, payload=request.json)
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(updated_game)


@GAMES_NAMESPACE.route("")
class Games(Resource):
    @GAMES_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        }
    )
    def get(self):
        """Fetch the games"""
        try:
            game = db_get_game()
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(game)


    @GAMES_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        }
    )
    @GAMES_NAMESPACE.expect(NEWGAME_MODEL, validate=True)
    @GAMES_NAMESPACE.response(200, "OK", GAME_MODEL)
    def put(self):
        """Add a new game"""
        try:
            game = game_put(payload=request.json)
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(game)


@GAMES_NAMESPACE.route("/<string:game_id>")
class GamesGamesId(Resource):
    @GAMES_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        }
    )
    def get(self, game_id):
        """Fetch the game <game_id>"""
        try:
            game = db_get_game(game_id=game_id)
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(game)
