"""API module."""
from publications_microservice import __version__
from flask_restx import Api, Resource, fields, reqparse
from publications_microservice.models import Publication, db
import operator as ops
from sqlalchemy import func
from .utils import FilterParam
from publications_microservice.exceptions import DistanceFilterMissingParameters

api = Api(
    prefix="/v1",
    version=__version__,
    title="Publications API",
    description="Publications microservice for bookbnb",
    default="Publications",
    default_label="Publications operations",
    validate=True,
)


@api.errorhandler(DistanceFilterMissingParameters)
def handle_user_does_not_exist(_error: DistanceFilterMissingParameters):
    """Handle missing distance params."""
    return (
        {
            "message": "Either all of max_distance, latitude and longitude should be passed to perform distance based filtering or none of them"
        },
        400,
    )


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = f"Error: {getattr(error, 'message', str(error))}"
    return {"message": message}, getattr(error, 'code', 500)


loc_model = api.model(
    "Location",
    {
        "latitude": fields.Float(description="latitude", required=True),
        "longitude": fields.Float(description="longitude", required=True),
    },
)

point_model = api.model(
    "Point",
    {
        "latitude": fields.Float(attribute=lambda x: db.session.scalar(func.ST_X(x))),
        "longitude": fields.Float(attribute=lambda x: db.session.scalar(func.ST_Y(x))),
    },
)

base_publication_model = api.model(
    'Base Publication',
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

new_publication_model = api.inherit(
    "New Publication Model",
    base_publication_model,
    {
        "loc": fields.Nested(
            loc_model, required=True, description="Location of the rental place",
        ),
    },
)


publication_model = api.inherit(
    'Created Publication',
    base_publication_model,
    {
        "loc": fields.Nested(point_model),
        "registered_date": fields.DateTime(description="Date of the publication"),
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
publication_parser.add_argument(
    "latitude",
    type=float,
    help="The latitude for the point near to look for. Note: max_distance and longitude are required when using latitude.",
    store_missing=True,
)
publication_parser.add_argument(
    "longitude",
    type=float,
    help="The longitude for the point near to look for. Note: max_distance and latitude are required when using longitude.",
    store_missing=True,
)
publication_parser.add_argument(
    "max_distance",
    type=float,
    help="The maximum distance (in km.) for the point near to look for. Note: latitude and longitude are required when using max_distance.",
    store_missing=True,
)


@api.route('/publications')
class PublicationListResource(Resource):
    @api.doc('list_publication')
    @api.marshal_list_with(publication_model)
    @api.expect(publication_parser)
    def get(self):
        """Get all publications."""
        params = publication_parser.parse_args()
        if params.max_distance is not None:
            has_lat_and_lon = (
                params.latitude is not None and params.longitude is not None
            )
            if not has_lat_and_lon:
                raise DistanceFilterMissingParameters
        query = Publication.query
        for _, filter_op in params.items():
            if not isinstance(filter_op, FilterParam):
                continue
            query = filter_op.apply(query, Publication)
        if params.max_distance:
            point = func.ST_GeographyFromText(
                f"POINT({params.latitude} {params.longitude})", srid=4326
            )

            query = query.filter(
                func.ST_DWithin(Publication.loc, point, params.max_distance * 1000)
            )
        return query.all()


@api.route('/users/<int:user_id>/publications')
@api.param('user_id', 'The user the new publication belongs to')
class CreatePublicationResource(Resource):
    @api.doc('create_publication')
    @api.expect(new_publication_model)
    @api.marshal_with(publication_model)
    def post(self, user_id):
        """Create a new publication."""
        data = api.payload
        # TODO: it'd be cool to marshal this on the model
        data['loc'] = f"POINT({data['loc']['latitude']} {data['loc']['longitude']})"
        data['user_id'] = user_id
        new_publication = Publication(**data)
        db.session.add(new_publication)
        db.session.commit()
        return new_publication

    @api.doc("list_user_publications")
    @api.marshal_list_with(publication_model)
    def get(self, user_id):
        """Get all publications from a user."""
        return Publication.query.filter(Publication.user_id == user_id).all()


@api.route('/publications/<int:publication_id>')
@api.param('publication_id', 'The publication unique identifier')
@api.response(404, 'Publication not found')
class PublicationResource(Resource):
    @api.doc('get_publication')
    @api.marshal_with(publication_model)
    def get(self, publication_id):
        """Get a publication by id."""
        return Publication.query.filter(Publication.id == publication_id).first()
