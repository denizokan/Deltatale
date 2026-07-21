from tkinter import PhotoImage

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

        self.kris_sprite_image = PhotoImage(file="sprites/characters/kris/spr_krisd_0.png")
        self.susie_sprite_image = PhotoImage(file="sprites/characters/susie/walk/spr_susied_0.png")

        kris_sprite = self.game.canvas.create_image(self.x, self.y, image=self.kris_sprite_image)
        susie_sprite = self.game.canvas.create_image(self.x + 30, self.y, image=self.susie_sprite_image)

        self.active_characters.extend([kris_sprite, susie_sprite])


    
    

