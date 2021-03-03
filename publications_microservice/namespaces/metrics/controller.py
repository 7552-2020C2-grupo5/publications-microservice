"""Metrics controller module."""

import logging
from datetime import date
from datetime import timedelta as td
from functools import wraps

from sqlalchemy import func

from publications_microservice.models import Publication

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def isodate(x):
    try:
        return date.fromisoformat(x)
    except TypeError:
        return x


def pad(count, start_date: date, end_date: date):
    dates = [x.get("date") for x in count]

    current_date = start_date

    while current_date <= end_date:
        if current_date not in dates:
            count.append({"date": current_date, "value": 0.0})
        current_date += td(days=1)

    count = sorted(count, key=lambda x: x.get("date"))

    return count


def data_map(count):
    return [{"date": isodate(rdate), "value": rval} for rdate, rval in count]


def prepare_metric(name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            count = f(*args, **kwargs)
            count = data_map(count)
            count = pad(count, *args)
            return {
                "name": name,
                "data": count,
            }

        return wrapper

    return decorator


@prepare_metric("new_publications_per_day")
def new_publications_per_day(start_date: date, end_date: date):
    count = (
        Publication.query.filter(
            func.date(Publication.publication_date).between(start_date, end_date)
        )
        .with_entities(
            func.date(Publication.publication_date), func.count(Publication.id)
        )
        .group_by(func.date(Publication.publication_date))
        .order_by(func.date(Publication.publication_date))
        .all()
    )
    return count


all_metrics = [new_publications_per_day]
