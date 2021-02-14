"""Constant values and defaults used in multiple modules."""
from enum import Enum


class BlockChainStatus(Enum):
    CONFIRMED = "CONFIRMED"
    DENIED = "DENIED"
    PENDING = "PENDING"
    UNSET = "UNSET"
    ERROR = "ERROR"
