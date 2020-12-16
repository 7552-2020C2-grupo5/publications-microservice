"""API module."""

from flask_restx import Api
from publications_microservice import __version__
from publications_microservice.namespaces.publications import (
    api as publications_namespace,
)
from publications_microservice.namespaces.questions import api as questions_namespace


api = Api(
    prefix="/v1",
    version=__version__,
    title="Publications API",
    description="Publications microservice for bookbnb",
    default="Publications",
    default_label="Publications operations",
    validate=True,
)

api.add_namespace(publications_namespace, path='/publications')
api.add_namespace(questions_namespace, path='/publications')


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = "Error: " + getattr(error, 'message', str(error))
    return {'message': message}, getattr(error, 'code', 500)
