"""API module."""
from publications_microservice import __version__
from flask_restx import Api, Resource, fields
from publications_microservice.models import Publication, db
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


api = Api(
    prefix="/v1",
    version=__version__,
    title="Publications API",
    description="Publications microservice for bookbnb",
    default="Publications",
    default_label="Publications operations",
    validate=True,
)


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = "Error: " + getattr(error, 'message', str(error))
    return {'message': message}, getattr(error, 'code', 500)


publication_model = api.model(
    'Publication',
    {
        "id": fields.Integer(
            readonly=True, description="The unique identifier of the publication"
        ),
        "title": fields.String(
            required=True, description="The title of the publication."
        ),
        "description": fields.String(
            required=True, name="A description of the publication"
        ),
        "rooms": fields.Integer(
            required=True,
            description="The amount of rooms in the published rental place.",
        ),
        "beds": fields.Integer(
            required=True,
            description="The amount of beds in the published rental place",
        ),
        "bathrooms": fields.Integer(
            required=True, description="The amount of bathrooms in the rental place"
        ),
        "price_per_night": fields.Float(
            required=True, description="How much a night costs in the rental place"
        ),
    },
)


@api.route('/publication')
class PublicationListResource(Resource):
    @api.doc('list_publication')
    @api.marshal_list_with(publication_model)
    def get(self):
        """Get all publications."""
        return Publication.query.all()

    @api.doc('create_publication')
    @api.expect(publication_model)
    @api.marshal_with(publication_model, envelope='resource')
    def post(self):
        """Create a new publication."""
        new_publication = Publication(**api.payload)
        db.session.add(new_publication)
        db.session.commit()
        return new_publication


@api.route('/publication/<int:publication_id>')
@api.param('Publication_id', 'The publication unique identifier')
@api.response(404, 'Publication not found')
class PublicationResource(Resource):
    @api.doc('get_publication')
    @api.marshal_with(publication_model, envelope='resource')
    def get(self, publication_id):
        """Get a publication by id."""
        publication = Publication.query.filter(Publication.id == publication_id).first()
        return publication
