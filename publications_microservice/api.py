"""API module."""
from publications_microservice import __version__
from flask_restx import Api, Resource, fields, reqparse
from publications_microservice.models import Publication, db
import operator as ops
from .utils import FilterParam

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
        "user_id": fields.Integer(readonly=True, description="Id of owner user"),
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


publication_parser = reqparse.RequestParser()
publication_parser.add_argument(
    "bathrooms",
    type=FilterParam("bathrooms", ops.ge),
    help="minimum amount of bathrooms needed",
    store_missing=False,
)
publication_parser.add_argument(
    "rooms",
    type=FilterParam("rooms", ops.ge),
    help="minimum amount of rooms needed",
    store_missing=False,
)
publication_parser.add_argument(
    "beds",
    type=FilterParam("beds", ops.ge),
    help="minimum amount of beds needed",
    store_missing=False,
)
publication_parser.add_argument(
    "price_per_night",
    type=FilterParam("price_per_night", ops.le),
    help="max price per night",
    store_missing=False,
)
publication_parser.add_argument(
    "user_id",
    type=FilterParam("user_id", ops.eq),
    help="id of owner user",
    store_missing=False,
)


@api.route('/publication')
class PublicationListResource(Resource):
    @api.doc('list_publication')
    @api.marshal_list_with(publication_model)
    @api.expect(publication_parser)
    def get(self):
        """Get all publications."""
        params = publication_parser.parse_args()
        api.app.logger.info("%s params", params)
        query = Publication.query
        for _, filter_op in params.items():
            query = filter_op.apply(query, Publication)
        return query.all()

    @api.doc('create_publication')
    @api.expect(publication_model)
    @api.marshal_with(publication_model)
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
    @api.marshal_with(publication_model)
    def get(self, publication_id):
        """Get a publication by id."""
        publication = Publication.query.filter(Publication.id == publication_id).first()
        return publication
