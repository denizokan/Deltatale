import json
import os
from tkinter import PhotoImage
from pygame import mixer
from src.core.enums import TextSound, Interactable

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
        self.is_paused = False
        self.debug_mode = False

        # Unpack room data
        bg_image_path = self.room_data["bg_image"]
        self.bg_image = PhotoImage(file=bg_image_path).zoom(2)

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

        # Draw interactables
        for interactable in self.interactables:
            interactable["interaction_count"] = 0
            if interactable["sprite"] != None:
                if len(interactable["sprite"]) > 1: # Its animated
                    interactable["image_obj"] = []
                    interactable["frame_index"] = 0
                    interactable["timer"] = 5
                    for sprite in interactable["sprite"]:
                        interactable_sprite = PhotoImage(file=sprite).zoom(2)
                        interactable["image_obj"].append(interactable_sprite)
                    canvas_id = self.game.canvas.create_image(interactable["x"] - self.game.camera.x, interactable["y"] - self.game.camera.y, image=interactable["image_obj"][0], anchor="center")
                else:
                    interactable_sprite = PhotoImage(file=interactable["sprite"]).zoom(2)
                    interactable["image_obj"] = interactable_sprite
                    canvas_id = self.game.canvas.create_image(interactable["x"] - self.game.camera.x, interactable["y"] - self.game.camera.y, image=interactable_sprite, anchor="center")
                interactable["canvas_id"] = canvas_id
                self.active_ui_elements.append(canvas_id)

    
    def is_position_free(self, target_x, target_y):
        """Returns 'False' if the next movement spot is occupied."""
        for wall in self.walls:
            coords = (wall["x1"], wall["y1"], wall["x2"], wall["y2"])
            x1, y1, x2, y2 = coords            
            if (x1 <= target_x <= x2 and y1 <= target_y <= y2): return False

        for interactable in self.interactables:
            obj_x = interactable["x"]
            obj_y = interactable["y"]

            if "img_obj" in interactable:
                half_w = interactable["img_obj"].width() / 2
                half_h = interactable["img_obj"].height() / 2
            else:
                half_w = 30
                half_h = 30

            x1, y1 = obj_x - half_w, obj_y - half_h
            x2, y2 = obj_x + half_w, obj_y + half_h

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
                next_room_id = self.room_data["exits"][index]["target_room"]
                
                try:
                    with open(self.path + next_room_id + ".json", "r") as file:
                        next_room_peek = json.load(file)
                    
                    if self.room_data["music"] != next_room_peek["music"]:
                        if hasattr(self, "music"):
                            self.music.fadeout(500)
                except Exception as e:
                    print(f"Warning: Could not read next room music: {e}")

                self.game.transition.fade_to_black(speed=24, on_complete=lambda: self.next_room(next_room_id))
                break


    def check_interactable(self):
        """Checks if the player is currently looking at an interactable. If yes, executes the interactable."""
        reach_distance = self.game.constants.REACH_DISTANCE

        reach = (self.game.player.x, self.game.player.y)
        if self.game.player.facing == "up":
            reach = (self.game.player.x, self.game.player.y - reach_distance)
        elif self.game.player.facing == "down":
            reach = (self.game.player.x, self.game.player.y + reach_distance)
        elif self.game.player.facing == "left":
            reach = (self.game.player.x - reach_distance, self.game.player.y)
        elif self.game.player.facing == "right":
            reach = (self.game.player.x + reach_distance, self.game.player.y)

        for interactable in self.interactables:
            if "image_obj" in interactable:
                obj_x, obj_y = interactable["x"], interactable["y"]
                if len(interactable["image_obj"]) > 1: # Animated
                    half_w = interactable["image_obj"][interactable["frame_index"]].width() / 2
                    half_h = interactable["image_obj"][interactable["frame_index"]].height() / 2
                else:
                    half_w = interactable["image_obj"].width() / 2
                    half_h = interactable["image_obj"].height() / 2
                
                x1, y1 = obj_x - half_w, obj_y - half_h
                x2, y2 = obj_x + half_w, obj_y + half_h

            else:
                x1, y1 = interactable["x1"], interactable["y1"]
                x2, y2 = interactable["x2"], interactable["y2"]

            if x1 <= reach[0] <= x2 and y1 <= reach[1] <= y2:
                self.play_interactable(interactable)
                break


    def play_interactable(self, interactable):
        """Plays the current interactable."""
        count = interactable["interaction_count"]
        interactable["interaction_count"] += 1
        text_groups = interactable["text"]

        selected_index = min(count, len(text_groups) - 1)
        chosen_dialogue = text_groups[selected_index]
        if interactable["type"] == Interactable.SAVE_POINT.value:
            mixer.Sound(file="sounds/sound_effects/snd_power.wav").play()
            self.game.dialogue_system.start_dialogue(
                text=chosen_dialogue,
                on_complete=lambda: self.game.save_screen.show_save_screen(interactable)
            )

    
    def next_room(self, next_room_id):
        """Cleans up and moves the player to the next room."""
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
            self.game.canvas.tag_raise(character)

        self.game.player.x = spawn_x
        self.game.player.y = spawn_y
        self.game.player.facing = spawn_facing
        self.game.player.anim_frame = 0
        self.game.player.anim_timer = 0
        self.game.player.history = [(spawn_x, spawn_y, spawn_facing, 0)] * self.game.player.follow_delay

        self.game.camera.update()
        self.game.player.draw(spawn_x, spawn_y, spawn_facing, 0)
        self.game.canvas.coords(self.game.current_room.background, -self.game.camera.x, -self.game.camera.y)

        if self.room_data["music"] != self.game.current_room.room_data["music"]:
            if hasattr(self.game.current_room, "music"):
                self.game.current_room.music.play(loops=-1)

        if self.debug_mode == True: # DEBUG MODE
            self.toggle_debug()
            self.game.current_room.toggle_debug()
        
        self.game.transition.fade_from_black(speed=24)


    def toggle_debug(self):
        """Toggles the debug mode on/off. Shows the colission points. 
        Blue: Walls, Green: Spawn Points, Red: Exit Points, Yellow: Interactables, Pink: Triggers"""
        if self.debug_mode == False:
            self.debug_mode = True
            self.debug_elements = []

            text_x = 10
            text_y = 20
            debug_text = self.game.canvas.create_text(
                text_x,
                text_y,
                text="DEBUG MODE",
                fill="white",
                font=("Determination Sans", 36, "normal"),
                anchor="w"
            )
            self.game.canvas.tag_raise(debug_text)
            self.debug_elements.append({"id": debug_text, "type": "text", "coords": (text_x, text_y)})

            coords_text_x = self.game.constants.WIDTH - 5
            coords_text_y = 15
            coords_text = self.game.canvas.create_text(
                coords_text_x,
                coords_text_y,
                text=f"{self.game.player.x}, {self.game.player.y}",
                fill="white",
                font=("Determination Sans", 24, "normal"),
                anchor="e"
            )
            self.game.canvas.tag_raise(coords_text)
            self.debug_elements.append({"id": coords_text, "type": "coords_text", "coords": (coords_text_x, coords_text_y)})

            self._create_rectangle(list=self.walls, color="blue", width=2)
            self._create_circle(list=self.spawns, radius=20, color="green")
            self._create_rectangle(list=self.exits, color="red", width=2)
            self._create_rectangle(list=self.interactables, color="yellow", width=2)
            self._create_rectangle(list=self.triggers, color="pink", width=2)

        else:
            self.debug_mode = False
            for element in self.debug_elements:
                self.game.canvas.delete(element["id"])
            self.debug_elements.clear()


    def _create_rectangle(self, list, color, width):
        coords_list = []
        for element in list:
            try:
                coords = (element["x1"], element["y1"], element["x2"], element["y2"])
            except KeyError: # Dealing with an interactable
                if "image_obj" in element:
                    obj_x, obj_y = element["x"], element["y"]
                    if len(element["image_obj"]) > 1:
                        half_w = element["image_obj"][element["frame_index"]].width() / 2
                        half_h = element["image_obj"][element["frame_index"]].height() / 2
                    else:
                        half_w = element["image_obj"].width() / 2
                        half_h = element["image_obj"].height() / 2
                    
                    x1, y1 = obj_x - half_w, obj_y - half_h
                    x2, y2 = obj_x + half_w, obj_y + half_h
    
                else:
                    x1, y1 = element["x1"], element["y1"]
                    x2, y2 = element["x2"], element["y2"]
                coords = (x1, y1, x2, y2)
            coords_list.append(coords)

        for element_box in coords_list:
            x1, y1, x2, y2 = element_box
            rectangle = self.game.canvas.create_rectangle(x1 - self.game.camera.x, y1 - self.game.camera.y, x2 - self.game.camera.x, y2 - self.game.camera.y, outline=color, width=width)
            self.debug_elements.append({"id": rectangle, "type": "rect", "coords": (x1, y1, x2, y2)})


    def _create_circle(self, list, radius, color):
        coords_list = []
        for element in list:
            coords = (element["x"], element["y"])
            coords_list.append(coords)

        for element_coords in coords_list:
            x, y = element_coords
            circle = self.game.canvas.create_oval((x - radius) - self.game.camera.x, (y - radius) - self.game.camera.y, (x + radius) - self.game.camera.x, (y + radius) - self.game.camera.y, fill=color)
            self.debug_elements.append({"id": circle, "type": "circle", "coords": (x, y, radius)})


    def update_positions(self):
        """Updates interactable indexes & positions in respect to camera x and y."""
        for interactable in self.interactables:
            canvas_id = interactable["canvas_id"]
            if len(interactable["image_obj"]) > 0:
                interactable["timer"] -= 1
                if interactable["timer"] <= 0:
                    interactable["frame_index"] += 1
                    if interactable["frame_index"] > len(interactable["image_obj"]) - 1:
                        interactable["frame_index"] = 0
                    interactable["timer"] = 5
                    self.game.canvas.itemconfig(canvas_id, image=interactable["image_obj"][interactable["frame_index"]])
            self.game.canvas.coords(canvas_id, interactable["x"] - self.game.camera.x, interactable["y"] - self.game.camera.y)

        if self.debug_mode: self._update_debug_positions() # DEBUG MODE
            

    def _update_debug_positions(self):
        """Updates the debug rectangles/circles positions to respect camera x and y."""
        for element in self.debug_elements:
            if element["type"] == "text":
                self.game.canvas.tag_raise(element["id"])

            if element["type"] == "coords_text":
                self.game.canvas.tag_raise(element["id"])
                self.game.canvas.itemconfig(element["id"], text=f"{self.game.player.x:.2f}, {self.game.player.y:.2f}")

            elif element["type"] == "rect":
                x1, y1, x2, y2 = element["coords"]
                self.game.canvas.coords(element["id"], x1 - self.game.camera.x, y1 - self.game.camera.y, x2 - self.game.camera.x, y2 - self.game.camera.y)

            elif element["type"] == "circle":
                x, y, radius = element["coords"]
                x1, y1, x2, y2 = x - radius, y - radius, x + radius, y + radius
                self.game.canvas.coords(element["id"], x1 - self.game.camera.x, y1 - self.game.camera.y, x2 - self.game.camera.x, y2 - self.game.camera.y)