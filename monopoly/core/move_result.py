from enum import Enum, auto

class MoveResult(Enum):
    CONTINUE = auto()
    BANKRUPT = auto()
    END_MOVE = auto()