"""Constant values and defaults used in multiple modules."""
from enum import Enum

DEFAULT_VERIFICATION_URL = (
    "https://tokens-microservice.herokuapp.com/v1/tokens/verification"
)
BOOKBNB_TOKEN = "bookbnb_token"


class BlockChainStatus(Enum):
    UNSET = "UNSET"
    CONFIRMED = "CONFIRMED"
    DENIED = "DENIED"
    PENDING = "PENDING"
    ERROR = "ERROR"
