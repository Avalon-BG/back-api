from uuid import uuid4

from flask import Blueprint, Flask
from marshmallow import Schema, fields

from flask_restx import Api, Resource


api_v1 = Blueprint("api", __name__, url_prefix="/api/1")

api = Api(api_v1, version="1.0", title="Todo API", description="A simple TODO API")

ns = api.namespace("todos", description="TODO operations")


# Class-style schema


class Task(Schema):
    description = fields.String(required=True, description="The task details")


class Todo(Schema):
    id = fields.String(required=True, description="The todo ID")
    task = fields.nested(Task, required=True)
    completed: fields.Boolean(required=True)
    created_at = fields.DateTime(required=True, format="iso")
    completed_at = fields.DateTime(format="iso")


# Dictionary-style schema (unchanged from user API perspective)

Todo = api.model(
    "Todo",
    {
        "id": fields.String(required=True, description="The todo ID"),
        "task": fields.nested(Task, required=True),
        "complete": fields.Boolean(required=True),
        "created_at": fields.DateTime(required=True, format="iso"),
        "completed_at": fields.DateTime(format="iso",),
    },
)


# Dummy definitions for demonstration purposes


def db_get_todo_or_abort(todo_id: str) -> dict:
    """ Fetch Todo from DB by id, abort with `404` if not found. """
    pass


@ns.route("/<string:todo_id>")
@api.doc(responses={404: "Todo not found"}, params={"todo_id": "The Todo ID"})
class Todo(Resource):
    """Show a single todo item and lets you delete them"""

    @api.marshal_with(Todo)
    def get(self, todo_id):
        """Fetch a given resource"""
        # Dict returned here is passed through Marshmallow schema for validation
        # and marshalling to JSON in the response
        data = db_get_todo_or_abort(todo_id)
        return data

    @api.expect(
        Task, location="form",
    )
    # Could also define inline as a Dict
    # @api.expect(
    #     {"task": fields.String(...)}, location="form",
    # )
    @api.marshal_with(Todo)
    def put(self, todo_id, task):
        """Update the task of a Todo"""
        # args automatically validated and passed in as an instance of Task -
        # no parser.parse_args
        data = db_update_todo(todo_id, task)  # Use the Marshmallow schema directly
        # Todo Marshmallow schema returned is automatically marhsalled into JSON
        # in the response
        return Todo(**data)


@ns.route("/")
class TodoList(Resource):
    """Shows a list of all todos, and lets you POST to add new tasks"""

    # Define some query params for filtering
    @api.expect(
        {"completed": fields.Boolean(), "completed_at": fields.DateTime(format="iso")},
        location="query",
    )
    # Marshal a list of a given schema
    @api.marshal_list_with(Todo)
    def get(self, args):
        """List all todos"""
        # Imagine this uses the filters in args properly to filter the result set
        # from the DB...
        return db_get_all("todo", filters=args)

    # Validate args with NewTodo schema then dump to a dict before passing
    # into handler
    @api.expect(Task, location="json", as_dict=True)
    @api.marshal_with(Todo, code=201)
    def post(self, args):
        """Create a todo"""
        # Just an example, I don't want to start a flame war around which values
        # should be used for IDs in a DB!
        todo_id = uuid4()
        # Do some work with args
        task = sanitise_input(args["task"])
        data = db_create_todo(str(todo_id), task)
        return data, 201


if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(api_v1)
    app.run(debug=True)
