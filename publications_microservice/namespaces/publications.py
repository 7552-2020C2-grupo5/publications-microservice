"""API module."""
import operator as ops

from flask_restx import Namespace, Resource, fields, reqparse
from sqlalchemy import func

from publications_microservice import __version__
from publications_microservice.exceptions import (
    BlockedPublication,
    DistanceFilterMissingParameters,
)
from publications_microservice.models import Publication, PublicationImage, db
from publications_microservice.namespaces.questions import publication_question_model
from publications_microservice.utils import FilterParam

api = Namespace("Publications", description="Publications operations")


@api.errorhandler(DistanceFilterMissingParameters)
def handle_missing_distance_parameters(_error: DistanceFilterMissingParameters):
    """Handle missing distance params."""
    return (
        {
            "message": "Either all of max_distance, latitude and longitude should be passed to perform distance based filtering or none of them"
        },
        400,
    )


@api.errorhandler(BlockedPublication)
def handle_publication_has_been_blocked(_error: BlockedPublication):
    """Handle blocked user."""
    return {"message": "The publication has been blocked"}, 403


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = f"Error: {getattr(error, 'message', str(error))}"
    return {"message": message}, getattr(error, 'code', 500)


publication_image_model = api.model(
    "Publication Image",
    {
        "url": fields.String(required=True, description="URL location for the image"),
        "id": fields.String(readonly=True, description="UUID for this image"),
    },
)

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
        "user_id": fields.Integer(description="Id of owner user"),
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
        "images": fields.List(
            fields.Nested(publication_image_model),
            required=True,
            description="List of images URLs",
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
        "publication_date": fields.DateTime(description="Date of the publication"),
        "questions": fields.List(
            fields.Nested(publication_question_model),
            description="Questions regarding the publication",
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
    "price_per_night_min",
    type=FilterParam("price_per_night_min", ops.ge, attribute="price_per_night"),
    help="min price per night",
    store_missing=False,
)
publication_parser.add_argument(
    "price_per_night_max",
    type=FilterParam("price_per_night_max", ops.le, attribute="price_per_night"),
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


@api.route('')
class PublicationsResource(Resource):
    @api.doc('create_publication')
    @api.expect(new_publication_model)
    @api.marshal_with(publication_model)
    def post(self):
        """Create a new publication."""
        data = api.payload
        # TODO: it'd be cool to marshal this on the model
        data['loc'] = f"POINT({data['loc']['latitude']} {data['loc']['longitude']})"

        images = []
        for img_data in data["images"]:
            new_img = PublicationImage(**img_data)
            images.append(new_img)
            db.session.add(new_img)
        data["images"] = images

        new_publication = Publication(**data)
        db.session.add(new_publication)
        db.session.commit()
        return new_publication

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
        query = Publication.query.filter(Publication.blocked == False)  # noqa: E712
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


@api.route('/<int:publication_id>')
@api.param('publication_id', 'The publication unique identifier')
@api.response(403, "Publication has been blocked")
class PublicationResource(Resource):
    @api.doc('get_publication')
    @api.response(200, "Publication found", model=publication_model)
    @api.response(404, 'Publication not found')
    def get(self, publication_id):
        """Get a publication by id."""
        publication = Publication.query.filter(Publication.id == publication_id).first()
        if publication is None:
            return {"message": "No publication was found by that id."}, 404
        if publication.blocked:
            raise BlockedPublication
        return api.marshal(publication, publication_model), 200

    @api.doc("put_publication")
    @api.response(200, "Publication found", model=publication_model)
    @api.response(404, 'Publication not found')
    @api.expect(new_publication_model)
    def put(self, publication_id):
        """Replace a publication by id."""
        publication = Publication.query.filter(Publication.id == publication_id).first()
        if publication is None:
            return {"message": "No publication was found by that id."}, 404
        if publication.blocked:
            raise BlockedPublication
        data = api.payload
        # TODO: it'd be cool to marshal this on the model
        data['loc'] = f"POINT({data['loc']['latitude']} {data['loc']['longitude']})"
        publication.update_from_dict(**data)
        db.session.merge(publication)
        db.session.commit()
        return api.marshal(publication, publication_model), 200

    @api.doc("block_publication")
    @api.response(200, "Publication successfully blocked")
    def delete(self, publication_id):
        """Block a publication."""
        publication = Publication.query.filter(Publication.id == publication_id).first()
        if publication is None:
            return {"message": "No publication was found by that id."}, 404
        if publication.blocked:
            raise BlockedPublication
        publication.blocked = True
        db.session.merge(publication)
        db.session.commit()
        return {"message": "Publication was successfully blocked"}, 200
