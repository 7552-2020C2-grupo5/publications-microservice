"""Custom exceptions."""


class DistanceFilterMissingParameters(Exception):
    pass


class BlockedPublication(Exception):
    pass


class PublicationDoesNotExist(Exception):
    pass


class ServerTokenError(Exception):
    pass


class UnsetServerToken(Exception):
    pass


class InvalidEnvironment(Exception):
    pass
