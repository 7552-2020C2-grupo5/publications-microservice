"""API module."""
import operator as ops

from flask_restx import Namespace, Resource, fields, reqparse
from sqlalchemy import func

from publications_microservice import __version__
from publications_microservice.constants import BlockChainStatus
from publications_microservice.exceptions import (
    BlockedPublication,
    DistanceFilterMissingParameters,
    PublicationDoesNotExist,
)
from publications_microservice.models import (
    Publication,
    PublicationImage,
    PublicationStar,
    db,
)
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


# https://github.com/python-restx/flask-restx/issues/268
# https://github.com/noirbizarre/flask-restplus/issues/707
# @api.errorhandler(BlockedPublication)
# def handle_publication_has_been_blocked(_error: BlockedPublication):
#    """Handle blocked user."""
#    return {"message": "The publication has been blocked"}, 403


@api.errorhandler(PublicationDoesNotExist)
def handle_publication_does_not_exist(_error: PublicationDoesNotExist):
    """Handle non-existing publication exception."""
    return {'message': "No publication by that id was found."}, 404


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

publication_patch_model = api.model(
    'Publication patch model',
    {
        "blockchain_status": fields.String(
            required=False,
            description="The status on the blockchain",
            enum=[x.value for x in BlockChainStatus],
            default=BlockChainStatus.UNSET.value,
            attribute='blockchain_status.value',
        ),
        "blockchain_transaction_hash": fields.String(
            required=False, description="The hash of the transaction on the blockchain"
        ),
        "blockchain_id": fields.Integer(
            required=False, description="The id on the blockchain"
        ),
    },
)

new_star_model = api.model(
    "Starred publication",
    {
        "user_id": fields.Integer(
            description="The unique identifier for the user starring the publication"
        ),
        "created_at": fields.DateTime(
            description="Time when the publication was starred"
        ),
        "publication_id": fields.Integer(
            description="The unique identifier for the publication being starred"
        ),
    },
)

publication_model = api.inherit(
    'Created Publication',
    base_publication_model,
    {
        "loc": fields.Nested(point_model),
        "publication_date": fields.DateTime(description="Date of the publication"),
        "blocked": fields.Boolean(description="Is blocked?"),
        "questions": fields.List(
            fields.Nested(publication_question_model),
            description="Questions regarding the publication",
        ),
        "blockchain_status": fields.String(
            required=False,
            description="The status on the blockchain",
            enum=[x.value for x in BlockChainStatus],
            default=BlockChainStatus.UNSET.value,
            attribute='blockchain_status.value',
        ),
        "blockchain_id": fields.Integer(description="The id on the blockchain"),
        "blockchain_transaction_hash": fields.String(
            description="The hash of the transaction on the blockchain"
        ),
        "stars": fields.List(
            fields.Nested(new_star_model), description="Stars given to the publication"
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
    type=FilterParam(
        "price_per_night_min", ops.ge, attribute="price_per_night", schema="number"
    ),
    help="min price per night",
    store_missing=False,
)
publication_parser.add_argument(
    "price_per_night_max",
    type=FilterParam(
        "price_per_night_max", ops.le, attribute="price_per_night", schema="number"
    ),
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
    "blockchain_status",
    type=FilterParam("blockchain_status", ops.eq, schema=str),
    help="blockchain_status",
    default=BlockChainStatus.CONFIRMED.value,
)
publication_parser.add_argument(
    "starring_user_id",
    type=FilterParam("starring_user_id", ops.eq, attribute="stars.user_id"),
    help="Id of starring user",
    store_missing=False,
)
publication_parser.add_argument(
    "blockchain_transaction_hash",
    type=FilterParam("blockchain_transaction_hash", ops.eq, schema=str),
    help="The hash of the transaction that created the publication on the blockchain",
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


def conditional_filter(attr, val):
    if val == True:  # noqa: E712
        return attr == False  # noqa: E712
    else:
        return 1 == 1


publication_parser.add_argument(
    "filter_blocked",
    type=FilterParam(
        "filter_blocked",
        conditional_filter,
        attribute="blocked",
        schema=bool,
        transform={"true": True, "false": False}.get,
    ),
    store_missing=True,
    default="true",
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
        has_lat = params.latitude is not None
        has_lon = params.longitude is not None
        has_dist = params.max_distance is not None

        if any((has_lat, has_lon, has_dist)) and not all((has_lat, has_lon, has_dist)):
            raise DistanceFilterMissingParameters

        query = Publication.query  # noqa: E712

        for filter_name, filter_op in params.items():
            print(f"filter_name: {filter_name}, filter_op: {filter_op}")
            if not isinstance(filter_op, FilterParam):
                print("filter ", filter_name, " is not magic, and op is ", filter_op)
                if filter_op is None:
                    continue
                for i in publication_parser.args:
                    if i.name == filter_name:
                        filter_op = i.type(filter_op)
                        break

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
    @api.response(403, "Publication blocked")
    def get(self, publication_id):
        """Get a publication by id."""
        publication = Publication.query.filter(Publication.id == publication_id).first()
        if publication is None:
            raise PublicationDoesNotExist
        if publication.blocked:
            return {"message": "Publication is blocked"}, 403
        return api.marshal(publication, publication_model), 200

    @api.doc("put_publication")
    @api.response(200, "Publication found", model=publication_model)
    @api.response(403, "Publication blocked")
    @api.response(404, 'Publication not found')
    @api.expect(new_publication_model)
    def put(self, publication_id):
        """Replace a publication by id."""
        publication = Publication.query.filter(Publication.id == publication_id).first()
        if publication is None:
            raise PublicationDoesNotExist
        if publication.blocked:
            return {"message": "Publication is blocked"}, 403

        data = api.payload
        # TODO: it'd be cool to marshal this on the model
        data['loc'] = f"POINT({data['loc']['latitude']} {data['loc']['longitude']})"

        for image in publication.images:
            db.session.delete(image)

        images = []
        for img_data in data["images"]:
            new_img = PublicationImage(**img_data)
            images.append(new_img)
            db.session.add(new_img)
        data["images"] = images

        publication.update_from_dict(**data)
        db.session.merge(publication)
        db.session.commit()
        return api.marshal(publication, publication_model), 200

    @api.doc("patch_publication")
    @api.response(200, "Publication found", model=publication_model)
    @api.response(404, 'Publication not found')
    @api.expect(publication_patch_model)
    def patch(self, publication_id):
        """Replace a publication by id."""
        publication = Publication.query.filter(Publication.id == publication_id).first()
        if publication is None:
            raise PublicationDoesNotExist
        if publication.blocked:
            raise BlockedPublication

        data = api.payload

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
            raise PublicationDoesNotExist
        if publication.blocked:
            raise BlockedPublication
        publication.blocked = True
        db.session.merge(publication)
        db.session.commit()
        return {"message": "Publication was successfully blocked"}, 200


publication_star_parser = reqparse.RequestParser()
publication_star_parser.add_argument(
    "user_id",
    type=FilterParam("user_id", ops.eq),
    help="Unique identifier for the user",
    store_missing=False,
)

publication_star_uid_parser = reqparse.RequestParser()
publication_star_uid_parser.add_argument(
    "user_id", type=int, help="Unique identifier for the user", required=True,
)


@api.route('/<int:publication_id>/star')
@api.param('publication_id', 'The publication unique identifier')
class PublicationStarResource(Resource):
    @api.doc('star_publication')
    @api.response(200, "Publication starred")
    @api.response(403, "Publication has been blocked")
    @api.response(404, 'Publication not found')
    @api.expect(publication_star_uid_parser)
    @api.marshal_with(new_star_model)
    def post(self, publication_id):
        """Star a publication."""
        publication = Publication.query.filter(Publication.id == publication_id).first()
        if publication is None:
            raise PublicationDoesNotExist
        if publication.blocked:
            raise BlockedPublication

        args = publication_star_uid_parser.parse_args()

        new_star = PublicationStar(user_id=args.user_id, publication_id=publication_id)
        db.session.add(new_star)
        db.session.commit()

        return new_star

    @api.doc('unstar_publication')
    @api.response(200, "Publication unstarred")
    @api.response(400, "Bad request")
    @api.expect(publication_star_uid_parser)
    def delete(self, publication_id):
        """Unstar a publication."""
        args = publication_star_uid_parser.parse_args()
        publication_star = PublicationStar.query.filter(
            PublicationStar.publication_id == publication_id,
            PublicationStar.user_id == args.user_id,
        ).first()
        if publication_star is None:
            return (
                {
                    "message": f"Publication {publication_id} was not starred by user {args.user_id}"
                },
                400,
            )
        db.session.delete(publication_star)
        db.session.commit()
        return {"message": "Successfully deleted"}, 200

    @api.doc('get_starrings')
    @api.marshal_list_with(new_star_model)
    @api.response(200, "Publications filtered")
    @api.response(400, "Bad request")
    @api.expect(publication_star_parser)
    def get(self, publication_id):
        """Get a starring."""
        params = publication_star_parser.parse_args()
        query = PublicationStar.query.filter(
            PublicationStar.publication_id == publication_id,
        )
        for _, filter_op in params.items():
            if not isinstance(filter_op, FilterParam):
                continue
            query = filter_op.apply(query, PublicationStar)
        return query.all()
