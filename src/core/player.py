from tkinter import PhotoImage
from src.core.enums import GameState, Action

class Player:
    """
    Handles player overworld movement and tracks the player position.
    """

    def __init__(self, main_game, start_x, start_y):
        self.game = main_game
        self.x = start_x
        self.y = start_y

        self.speed = self.game.constants.PLAYER_SPEED

        self.active_characters = []
        self.active_ui_elements = []

        self.kris_sprite_image = PhotoImage(file="sprites/characters/kris/spr_krisd_0.png").zoom(2)
        self.susie_sprite_image = PhotoImage(file="sprites/characters/susie/walk/spr_susied_0.png").zoom(2)

        kris_sprite = self.game.canvas.create_image(self.x, self.y, image=self.kris_sprite_image)
        susie_sprite = self.game.canvas.create_image(self.x + 60, self.y, image=self.susie_sprite_image)

        self.active_characters.extend([kris_sprite, susie_sprite])


    def update(self, input_mgr):
        """Handles inputs and modifies the player sprite."""
        dx, dy = 0, 0

        if input_mgr.is_pressed(Action.UP):    dy = -self.speed
        if input_mgr.is_pressed(Action.DOWN):  dy = self.speed
        if input_mgr.is_pressed(Action.LEFT):  dx = -self.speed
        if input_mgr.is_pressed(Action.RIGHT): dx = self.speed

        if (dx != 0 or dy != 0):
            self.draw(dx, dy)

    
    def draw(self, x, y):
        """Moves the player sprite to the given coordinates."""
        self.x += x
        self.y += y

        kris_sprite = self.active_characters[0]
        susie_sprite = self.active_characters[1]

        self.game.canvas.coords(kris_sprite, self.x, self.y)
        self.game.canvas.coords(susie_sprite, self.x + 60, self.y)