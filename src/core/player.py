from tkinter import PhotoImage
from src.core.enums import Action

class Player:
    """
    Handles player overworld movement and tracks the player position.
    """

    def __init__(self, main_game, start_x, start_y):
        self.game = main_game
        self.x = start_x
        self.y = start_y

        self.speed = self.game.constants.PLAYER_SPEED
        self.facing = "down"

        self.active_characters = []
        self.active_ui_elements = []

        self.follow_delay = 15
        self.history = [(self.x, self.y, self.facing)] * self.follow_delay

        self.kris_sprites = {
            "down": PhotoImage(file="sprites/characters/kris/spr_krisd_0.png").zoom(2),
            "up": PhotoImage(file="sprites/characters/kris/spr_krisu_0.png").zoom(2),
            "left": PhotoImage(file="sprites/characters/kris/spr_krisl_0.png").zoom(2),
            "right": PhotoImage(file="sprites/characters/kris/spr_krisr_0.png").zoom(2)
        }
        
        self.susie_sprites = {
            "down": PhotoImage(file="sprites/characters/susie/walk/spr_susied_0.png").zoom(2),
            "up": PhotoImage(file="sprites/characters/susie/walk/spr_susieu_0.png").zoom(2),
            "left": PhotoImage(file="sprites/characters/susie/walk/spr_susiel_0.png").zoom(2),
            "right": PhotoImage(file="sprites/characters/susie/walk/spr_susier_0.png").zoom(2)
        }

        kris_sprite = self.game.canvas.create_image(self.x, self.y, image=self.kris_sprites["down"])
        susie_sprite = self.game.canvas.create_image(self.x, self.y, image=self.susie_sprites["down"])

        self.active_characters.extend([kris_sprite, susie_sprite])


    def update(self, input_mgr):
        """Handles inputs and modifies the player sprite."""
        if self.game.transition.is_transitioning:
            return
        
        dx, dy = 0, 0
        new_facing = self.facing

        active_key = input_mgr.get_active_direction()
        speed_mult = 1

        if input_mgr.is_pressed(Action.CANCEL):
            speed_mult = 1.6

        if active_key == "Up":
            dy = -self.speed * speed_mult
            new_facing = "up"
        elif active_key == "Down":
            dy = self.speed * speed_mult
            new_facing = "down"
        elif active_key == "Left":
            dx = -self.speed * speed_mult
            new_facing = "left"
        elif active_key == "Right":
            dx = self.speed * speed_mult
            new_facing = "right"

        if (dx != 0 or dy != 0):
            self.facing = new_facing
            self.move(dx, dy)

    
    def move(self, dx, dy):
        """Records history, applies movement, and triggers the draw sequence."""
        self.history.append((self.x, self.y, self.facing))
        if len(self.history) > self.follow_delay:
            self.history.pop(0)

        self.x += dx
        self.y += dy

        sx, sy, s_facing = self.history[0]

        self.draw(sx, sy, s_facing)

    def draw(self, sx, sy, s_facing):
        """Updates the canvas coordinates and images for all party members."""
        # Update Kris
        self.game.canvas.coords(self.active_characters[0], self.x, self.y)
        self.game.canvas.itemconfig(self.active_characters[0], image=self.kris_sprites[self.facing])
        
        # Update Susie
        self.game.canvas.coords(self.active_characters[1], sx, sy)
        self.game.canvas.itemconfig(self.active_characters[1], image=self.susie_sprites[s_facing])

        if self.y > sy: # Kris is below Susie
            self.game.canvas.tag_raise(self.active_characters[0])
        else:
            self.game.canvas.tag_raise(self.active_characters[1])
