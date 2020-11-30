"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2.types import Geography
from sqlalchemy.sql import func

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
