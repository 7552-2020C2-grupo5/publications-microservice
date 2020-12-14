"""API module."""
from publications_microservice import __version__
from flask_restx import Resource, Namespace

api = Namespace("Questions", description="Publication questions operations")


@api.route("/questions")
class PublicationQuestionListResource(Resource):
    def post(self):
        pass

    def get(self):
        pass


@api.route("/questions/<int:question_id>")
class PublicationResource(Resource):
    def get(self, question_id):
        pass

    def put(self, question_id):
        pass
