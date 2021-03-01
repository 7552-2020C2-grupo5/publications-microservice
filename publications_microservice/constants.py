"""Constant values and defaults used in multiple modules."""
from enum import Enum

DEFAULT_VERIFICATION_URL = (
    "https://tokens-microservice.herokuapp.com/v1/tokens/verification"
)


class BlockChainStatus(Enum):
    UNSET = "UNSET"
    CONFIRMED = "CONFIRMED"
    DENIED = "DENIED"
    PENDING = "PENDING"
    ERROR = "ERROR"
