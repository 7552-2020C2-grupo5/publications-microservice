"""Metrics namespace module."""

from flask_restx import Namespace, Resource

from .controller import all_metrics
from .models import metric_datum_model, metric_model
from .parsers import metrics_parser

ns = Namespace("Metrics", description="Metrics operations",)


ns.models[metric_datum_model.name] = metric_datum_model
ns.models[metric_model.name] = metric_model


@ns.route('')
class MetricsListResource(Resource):
    @ns.doc('list_metrics')
    @ns.marshal_list_with(metric_model)
    @ns.expect(metrics_parser)
    def get(self):
        """Get all metrics."""
        params = metrics_parser.parse_args()
        return [m(params.start_date, params.end_date) for m in all_metrics]
