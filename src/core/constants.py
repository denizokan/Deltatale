class Constants:
    """
    These values can be accessed anywhere.

    Usage:
    ```
    from src.core.constants import Constants

    Constants.FPS # Returns the FPS value.
    ```
    """

    FPS = 30
    WIDTH = 640
    HEIGHT = 480

    PLAYER_SPEED = 4
    SOUL_SPEED = 4.5
    REACH_DISTANCE = 30
    DEFAULT_TYPEWRITER_TIMER = 1


class Color:
    """
    Stores most used colors with their RGB values.

    Usage:
    ```
    from src.core.constants import Color
    
    Color.RED # Returns the RGB value.
    ```
    """

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 255, 0)
    GREEN = (0, 0, 255)
    YELLOW = (255, 0, 255)
    MAGENTA = (255, 255, 0)
    CYAN = (0, 255, 255)