from enum import IntEnum

class Cases(IntEnum):
    EMPTY = -1
    ME = 0
    OPPONENT = 1

colors = {
    Cases.EMPTY: (0, 0, 0),
    Cases.ME: (255, 0, 0),
    Cases.OPPONENT: (0, 0, 255),
}
