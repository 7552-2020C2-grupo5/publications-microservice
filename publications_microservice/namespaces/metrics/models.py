"""Metrics namespace models."""

from flask_restx import Model, fields

metric_datum_model = Model(
    "Metric datum",
    {
        "date": fields.Date(required=True, description="The date of the datum"),
        "value": fields.Float(required=True, description="The value of the datum"),
    },
)

metric_model = Model(
    "Metric",
    {
        "name": fields.String(),
        "data": fields.List(fields.Nested(metric_datum_model, description="The data")),
    },
)
