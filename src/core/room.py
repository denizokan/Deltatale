import json
import os
from tkinter import PhotoImage
from pygame import mixer

class Room:
    """Initializes a room."""
    def __init__(self, main_game, room_id):
        self.game = main_game
        self.room_id = room_id
        self.path = "data/rooms/"

        try:
            with open(self.path + self.room_id + ".json", "r") as file:
                self.room_data = json.load(file)
        except Exception as e:
            raise RuntimeError(f"An error has occured while trying to read room data for {self.room_id}.") from e

        self.active_ui_elements = []

        # Unpack room data
        bg_image_path = self.room_data["bg_image"]
        self.bg_image = PhotoImage(file=bg_image_path)

        if self.room_data["music"] is not None: self.music = mixer.Sound(file=self.room_data["music"])
        
        self.walls = self.room_data["walls"]
        self.spawns = self.room_data["spawns"]
        self.exits = self.room_data["exits"]
        self.triggers = self.room_data["triggers"]
        self.interactables = self.room_data["interactables"]

        # Draw the background
        self.background = self.game.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.game.canvas.tag_lower(self.background)
        self.active_ui_elements.append(self.background)

    
    def is_position_free(self, target_x, target_y):
        """Returns 'False' if the next movement spot is occupied."""
        coords_list = []
        for wall in self.walls:
            coords = (wall["x1"], wall["y1"], wall["x2"], wall["y2"])
            coords_list.append(coords)

        for box in coords_list:
            x1, y1, x2, y2 = box
            if (x1 <= target_x <= x2 and y1 <= target_y <= y2): return False

        return True
    

    def check_exit(self, target_x, target_y):
        """Checks if player is stepping on an exit. If so, calls the 'next_room()' method."""
        coords_list = []
        for exit in self.exits:
            coords_list.append((exit["x1"], exit["y1"], exit["x2"], exit["y2"]))

        for index, box in enumerate(coords_list):
            x1, y1, x2, y2 = box
            if (x1 <= target_x <= x2 and y1 <= target_y <= y2):
                self.game.transition.fade_to_black(speed=8, on_complete=lambda: self.load_next_room(index))
                break

    
    def next_room(self, exit_index):
        """Cleans up and moves the player to the next room."""
        next_room_id = self.room_data["exits"][exit_index]["target_room"]

        for element in self.active_ui_elements:
            self.game.canvas.delete(element)

        self.active_ui_elements.clear()
        self.game.current_room = Room(self.game, next_room_id)

        spawn_x, spawn_y, spawn_facing = 0, 0, "right"
        for spawn in self.game.current_room.room_data["spawns"]:
            if spawn["from_room"] == self.room_id:
                spawn_x = spawn["x"]
                spawn_y = spawn["y"]
                spawn_facing = spawn["facing"]
                break

        for character in self.game.player.active_characters:
            self.game.canvas.coords(character, spawn_x, spawn_y)

        self.game.player.x = spawn_x
        self.game.player.y = spawn_y
        self.game.player.facing = spawn_facing

        self.game.player.anim_frame = 0
        self.game.player.anim_timer = 0
        self.game.player.history.clear()
        self.game.canvas.itemconfig(self.game.player.kris_sprite, image=self.game.player.kris_sprites[spawn_facing][0])
        self.game.canvas.itemconfig(self.game.player.susie_sprite, image=self.game.player.susie_sprites[spawn_facing][0])
        
        self.game.transition.fade_from_black()