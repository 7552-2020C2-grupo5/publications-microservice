"""Logic for questions."""

from publications_microservice.exceptions import (
    BlockedPublication,
    PublicationDoesNotExist,
)
from publications_microservice.models import Publication


def validate_publication(publication_id):
    """Validate a publicarion from payload."""
    publication = Publication.query.filter(Publication.id == publication_id).first()
    if publication is None:
        raise PublicationDoesNotExist
    if publication.blocked:
        raise BlockedPublication
