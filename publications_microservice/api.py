"""API module."""

from flask_restx import Api

from publications_microservice import __version__
from publications_microservice.namespaces.metrics import api as metrics_namespace
from publications_microservice.namespaces.publications import (
    api as publications_namespace,
)
from publications_microservice.namespaces.questions import api as questions_namespace
from publications_microservice.namespaces.token import api as token_namespace

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
api.add_namespace(token_namespace, path='/token')
api.add_namespace(metrics_namespace, path="/metrics")


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = f"Error: {getattr(error, 'message', str(error))}"
    return {"message": message}, getattr(error, 'code', 500)
