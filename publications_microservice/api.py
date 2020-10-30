"""API module."""
from flask_restx import Api
from publications_microservice import __version__
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


api = Api(prefix="/v1", version=__version__)
