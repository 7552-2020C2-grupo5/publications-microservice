"""Metrics namespace parsers."""

from flask_restx import inputs, reqparse

metrics_parser = reqparse.RequestParser()
metrics_parser.add_argument(
    "start_date", type=inputs.date_from_iso8601, help="initial date", required=True
)
metrics_parser.add_argument(
    "end_date", type=inputs.date_from_iso8601, help="final date", required=True
)
