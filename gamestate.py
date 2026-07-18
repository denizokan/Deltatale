from enum import Enum

class GameState(Enum):
    """
    All possible game states. Check with GameState.VALUE
    """

    MENU = 1
    PLAYING = 2
    BATTLE = 3
    GAMEOVER = 4