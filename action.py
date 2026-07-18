from enum import Enum

class Action(Enum):
    """
    All possible events that can occur while in game. Check with is_pressed(Action.STATE)
    """

    # Menu
    CONFIRM = 1
    CANCEL = 2
    MENU = 3
    FULLSCREEN = 4
    QUIT = 5

    # Movement
    UP = 6
    DOWN = 7
    LEFT = 8
    RIGHT = 9