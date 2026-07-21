class Camera:
    """For tracking the player."""
    def __init__(self, main_game):
        self.game = main_game
        self.screen_width = self.game.constants.WIDTH
        self.screen_height = self.game.constants.HEIGHT