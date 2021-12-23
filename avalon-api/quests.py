from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_restx import Namespace, Resource, fields

from avalonBG.db_utils import db_connect, db_get_table
from avalonBG.exception import AvalonBGError
from avalonBG.quests import quest_delete, quest_get, quest_post, quest_put, quest_unsend

from api_utils import HTTPError

# pylint: disable=R0201


QUESTS_BLUEPRINT = Blueprint("quests", __name__)
CORS(QUESTS_BLUEPRINT)

QUESTS_BLUEPRINT.before_request(db_connect)


QUESTS_NAMESPACE = Namespace(name="quests", description="Quests operations", path="/games")



wild = fields.Wildcard(fields.Integer)
from collections import OrderedDict
mod = OrderedDict()
mod["*"] = wild
quests_send_post = QUESTS_NAMESPACE.model(
    "Quests send post",
    mod
)

quests_send_post = QUESTS_NAMESPACE.model(
    "Quests send post",
    {
        "": fields.Boolean(
            required=True,
            description="Vote of the player"
        )
    }
)

# quests_send_put = QUESTS_NAMESPACE.model(
#     "Quests send put",
#     [
#         fields.String(
#             required=True,
#             description="Id of the player",
#             example="94ee4546-9358-4a68-a155-01876a7c583f"
#         )
#     ]
# )


@QUESTS_NAMESPACE.route("/quests")
class Quests(Resource):
    @QUESTS_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        },
        params={
            "game_id": "Specify the Id associated with the game"
        }
    )
    def get(self):
        """Fetch the quests"""
        try:
            table_quests = db_get_table(table_name="quests")
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(table_quests)


@QUESTS_NAMESPACE.route("/<string:game_id>/quest_unsend")
class QuestsUnsend(Resource):
    @QUESTS_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        },
        params={
            "game_id": "Specify the Id associated with the game"
        }
    )
    def post(self, game_id):
        """This function sends new quest of the game <game_id>"""
        try:
            game_updated = quest_unsend(game_id=game_id)
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(game_updated)


@QUESTS_NAMESPACE.route("/<string:game_id>/quests/<int:quest_number>")
class QuestsSend(Resource):
    @QUESTS_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        },
        params={
            "game_id": "Specify the Id associated with the game",
            "quest_number": "Specify the number of the quest (between 0 and 4)"
        }
    )
    def delete(self, game_id, quest_number):
        """This function sends new quest of the game <game_id>"""
        try:
            game_updated = quest_delete(
                game_id=game_id,
                quest_number=quest_number
            )
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(game_updated)

    @QUESTS_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        },
        params={
            "game_id": "Specify the Id associated with the game",
            "quest_number": "Specify the number of the quest (between 0 and 4)"
        }
    )
    def get(self, game_id, quest_number):
        """This function sends new quest of the game <game_id>"""
        try:
            game_updated = quest_get(
                game_id=game_id,
                quest_number=quest_number
            )
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(game_updated)

    @QUESTS_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        },
        params={
            "game_id": "Specify the Id associated with the game",
            "quest_number": "Specify the number of the quest (between 0 and 4)"
        }
    )
    @QUESTS_NAMESPACE.expect(quests_send_post)
    def post(self, game_id, quest_number):
        """This function sends new quest of the game <game_id>"""
        try:
            game_updated = quest_post(
                payload=request.json,
                game_id=game_id,
                quest_number=quest_number
            )
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(game_updated)

    @QUESTS_NAMESPACE.doc(
        responses={
            200: "OK",
            400: "Invalid Argument"
        },
        params={
            "game_id": "Specify the Id associated with the game",
            "quest_number": "Specify the number of the quest (between 0 and 4)"
        }
    )
    # @QUESTS_NAMESPACE.expect(quests_send_put)
    def put(self, game_id, quest_number):
        """This function sends new quest of the game <game_id>"""
        try:
            game_updated = quest_put(
                payload=request.json,
                game_id=game_id,
                quest_number=quest_number
            )
        except AvalonBGError as error:
            raise HTTPError(str(error), status_code=400) from error

        return jsonify(game_updated)
