from enum import Enum

class GameStatus(Enum):
    NO_MATCH = 1
    FINISHED = 2
    WAITING_LOCAL_MOVE = 3
    OCURRING_LOCAL_MOVE = 4
    WAITING_REMOTE_MOVE = 5
    ABANDONED = 6
