

from enum import IntEnum, StrEnum


class ALLOCATION(IntEnum):
    STACK = 0
    HEAP = 1



class PASSING(IntEnum):
    REFERENCE = 0
    VALUE = 1


class OperatorKind(StrEnum):
    SUM = "+"
    MINUS = "-"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    