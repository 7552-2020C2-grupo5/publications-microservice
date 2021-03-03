"""API module."""
from datetime import datetime as dt

from flask_restx import Namespace, Resource, fields

from publications_microservice import __version__
from publications_microservice.controllers.questions import validate_publication
from publications_microservice.exceptions import (
    BlockedPublication,
    PublicationDoesNotExist,
)
from publications_microservice.models import PublicationQuestion, db

api = Namespace("Questions", description="Publication questions operations")


@api.errorhandler(BlockedPublication)
def handle_blocked_publication_questions(_exception):
    """Handle blocked publication exception."""
    return {'message': "Publication is blocked"}, 400


@api.errorhandler(PublicationDoesNotExist)
def handle_publication_does_not_exist(_error: PublicationDoesNotExist):
    """Handle non-existing publication exception."""
    return {'message': "No publication by that id was found."}, 404


new_publication_question_model = api.model(
    "New Publication Question",
    {
        "question": fields.String(
            description="The question being asked", required=True
        ),
        "user_id": fields.Integer(
            description="The user asking the question", required=True
        ),
    },
)

publication_question_model = api.clone(
    "Publication Model",
    new_publication_question_model,
    {
        "id": fields.Integer(
            description="The unique identifier for the question", readonly=True
        ),
        "reply": fields.String(description="The reply to the question", required=False),
        "created_at": fields.DateTime(
            description="Timestamp the question was asked at"
        ),
        "replied_at": fields.DateTime(description="Timestamp the question was replied"),
    },
)

reply_model = api.model(
    "Reply model",
    {"reply": fields.String(description="The reply to the question", required=True)},
)


@api.route("/<int:publication_id>/questions")
@api.param("publication_id", "The publication unique identifier")
class PublicationQuestionListResource(Resource):
    """Publication list resource."""

    @api.doc("create_question")
    @api.marshal_with(publication_question_model)
    @api.expect(new_publication_question_model)
    @api.response(404, "Publication not found")
    @api.response(400, "Publication has been blocked")
    def post(self, publication_id):
        """Create a new publication question."""
        data = api.payload
        validate_publication(publication_id)

        new_question = PublicationQuestion(**data, publication_id=publication_id)
        db.session.add(new_question)
        db.session.commit()
        return new_question


@api.route("/<int:publication_id>/questions/<int:question_id>")
@api.param("publication_id", "The publication unique identifier")
@api.param("question_id", "The question unique identifier")
class PublicationResource(Resource):
    """Publication Resource."""

    @api.doc("reply_question")
    @api.expect(reply_model)
    @api.response(200, "Question updated")
    @api.response(404, "Resource not found")
    def patch(self, publication_id, question_id):
        """Patch a publication question."""
        validate_publication(publication_id)
        question = PublicationQuestion.query.filter(
            PublicationQuestion.id == question_id,
            PublicationQuestion.publication_id == publication_id,
        ).first()
        if question is None:
            return {"message": "No question was found by that id"}, 404
        question.reply = api.payload["reply"]
        question.replied_at = dt.now()
        db.session.merge(question)
        db.session.commit()
        return api.marshal(question, publication_question_model), 200
