"""SQLAlchemy models."""
from uuid import uuid4

from flask_sqlalchemy import SQLAlchemy
from geoalchemy2.types import Geography
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from publications_microservice.constants import BlockChainStatus

db = SQLAlchemy()


class Publication(db.Model):  # type: ignore
    """Publications model."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String)
    description = db.Column(db.String)
    rooms = db.Column(
        db.Integer, db.CheckConstraint('rooms >= 0', name='rooms_nonnegative')
    )
    beds = db.Column(
        db.Integer, db.CheckConstraint('beds >= 0', name='beds_nonnegative')
    )
    bathrooms = db.Column(
        db.Integer, db.CheckConstraint('bathrooms >= 0', name='bathrooms_nonnegative')
    )
    price_per_night = db.Column(
        db.Numeric,
        db.CheckConstraint('price_per_night > 0', name='price_per_night_nonnegative'),
    )
    loc = db.Column(Geography(geometry_type='POINT', srid=4326))
    publication_date = db.Column(db.DateTime, nullable=False, default=func.now())
    blocked = db.Column(db.Boolean, default=False)
    blockchain_status = db.Column(
        db.Enum(BlockChainStatus), nullable=False, default=BlockChainStatus.UNSET.value,
    )
    blockchain_transaction_hash = db.Column(db.String(512), nullable=True)
    blockchain_id = db.Column(db.Integer, nullable=True)

    images = db.relationship("PublicationImage", backref="publication", lazy=True)
    questions = db.relationship("PublicationQuestion", backref="publication", lazy=True)
    stars = db.relationship("PublicationStar", backref="publication", lazy=True)

    def update_from_dict(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)


class PublicationImage(db.Model):  # type: ignore
    """Images for publications."""

    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    url = db.Column(db.String, nullable=False)
    publication_id = db.Column(
        db.Integer, db.ForeignKey('publication.id'), nullable=False
    )

    # TODO: validate URLs


class PublicationQuestion(db.Model):  # type: ignore
    """Public questions for publications."""

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    reply = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    replied_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, nullable=False)
    publication_id = db.Column(
        db.Integer, db.ForeignKey('publication.id'), nullable=False
    )


class PublicationStar(db.Model):  # type: ignore
    """Publication stars."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    publication_id = db.Column(
        db.Integer, db.ForeignKey('publication.id'), nullable=False
    )
