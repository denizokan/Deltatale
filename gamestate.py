from enum import Enum

class GameState(Enum):
    """
    All possible game states. Check with GameState.VALUE
    """

    INTRO = 0
    FILE_SELECT = 1
    PLAYING = 2
    BATTLE = 3
    GAMEOVER = 4