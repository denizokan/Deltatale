import json
import time
import pygame
from pygame import mixer
from src.core.constants import Constants
from src.core.enums import Event, Interactable
from src.core.events import EventBus

class Room:
    """Initializes a room."""
    def __init__(self, room_id, asset_manager):
        self.room_id = room_id
        self.asset_manager = asset_manager

        path = "data/rooms/"

        try:
            with open(path + self.room_id + ".json", "r") as file:
                self.room_data = json.load(file)
        except Exception as e:
            raise RuntimeError(f"An error has occured while trying to read room data for {self.room_id}.") from e

        self.debug_mode = False

        # Unpack room data
        self.bg_image = self.asset_manager.get_image(self.room_data["bg_image"])

        if self.room_data["music"] is not None: self.music = mixer.Sound(file=self.room_data["music"])
        
        self.walls = self.room_data["walls"]
        self.spawns = self.room_data["spawns"]
        self.exits = self.room_data["exits"]
        self.triggers = self.room_data["triggers"]
        self.interactables = self.room_data["interactables"]

        # Draw interactables
        for interactable in self.interactables:
            if not self._isActive(interactable): continue

            interactable["interaction_count"] = 0
            if interactable["sprite"] != None:
                if interactable.get("is_animated", False): # Its animated
                    interactable["image_obj"] = []
                    interactable["frame_index"] = 0
                    interactable["timer"] = 5
                    interactable_sprites = self.asset_manager.get_image(interactable["sprite"])
                    interactable["image_obj"].extend(interactable_sprites)
                else:
                    interactable_sprite = self.asset_manager.get_image(interactable["sprite"])
                    interactable["image_obj"] = interactable_sprite

    
    def is_position_free(self, target_x, target_y):
        """Returns 'False' if the next movement spot is occupied."""
        for wall in self.walls:
            coords = (wall["x1"], wall["y1"], wall["x2"], wall["y2"])
            x1, y1, x2, y2 = coords            
            if (x1 <= target_x <= x2 and y1 <= target_y <= y2): return False

        for interactable in self.interactables:
            if not self._isActive(interactable): continue

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


    def check_trigger(self, target_x, target_y):
        """Checks if the player has stepped on an active cutscene trigger."""
        for index, trigger in enumerate(self.triggers):
            trigger_id = self.room_data["triggers"][index]["id"]

            if self.game.flags.get(f"cutscene_{trigger_id}_completed", False):
                continue

            x1, y1, x2, y2 = trigger["x1"], trigger["y1"], trigger["x2"], trigger["y2"]
            
            if (x1 <= target_x <= x2 and y1 <= target_y <= y2):
                EventBus.emit(Event.START_CUTSCENE, trigger_id)
                break
    

    def check_exit(self, target_x, target_y):
        """Checks if player is stepping on an exit. If so, calls the 'next_room()' method."""
        coords_list = []
        for exit in self.exits:
            coords_list.append((exit["x1"], exit["y1"], exit["x2"], exit["y2"]))

        for index, box in enumerate(coords_list):
            x1, y1, x2, y2 = box
            if (x1 <= target_x <= x2 and y1 <= target_y <= y2):
                next_room_id = self.room_data["exits"][index]["target_room"]
                EventBus.emit(Event.CHANGE_ROOM, next_room_id)
                break


    def check_interactable(self, x, y, facing):
        """Checks if the player is currently looking at an interactable. If yes, executes the interactable."""
        reach_distance = Constants.REACH_DISTANCE

        reach = (x, y)
        if facing == "up":
            reach = (x, y - reach_distance)
        elif facing == "down":
            reach = (x, y + reach_distance)
        elif facing == "left":
            reach = (x - reach_distance, y)
        elif facing == "right":
            reach = (x + reach_distance, y)

        for interactable in self.interactables:
            if not self._isActive(interactable): continue

            if "image_obj" in interactable:
                obj_x, obj_y = interactable["x"], interactable["y"]
                if len(interactable["image_obj"]) > 1: # Animated
                    half_w = interactable["image_obj"][interactable["frame_index"]].get_width() / 2
                    half_h = interactable["image_obj"][interactable["frame_index"]].get_height() / 2
                else:
                    half_w = interactable["image_obj"].get_width() / 2
                    half_h = interactable["image_obj"].get_height() / 2
                
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
        count = interactable.get("interaction_count", 0)
        interactable["interaction_count"] = count + 1

        raw_text_data = interactable.get("text", [])
        if len(raw_text_data) == 0:
            return

        if interactable.get("type") == Interactable.SAVE_POINT.value:
            EventBus.emit(Event.PLAY_SOUND, "snd_power")

        dialogue_data = {
            "text": raw_text_data,
            "interaction_index": count,
            "type": interactable.get("type"),
            "interactable": interactable,
            "actors": {interactable["name"]: interactable} if interactable.get("type") == Interactable.NPC.value else None
        }
        EventBus.emit(Event.START_DIALOGUE, dialogue_data)


    def toggle_debug(self):
        """Toggles the debug mode on/off."""
        self.debug_mode = not self.debug_mode


    def update(self):
        """Updates interactable indexes & positions in respect to camera x and y."""
        for interactable in self.interactables:
            if interactable.get("is_battling", False): continue
            if not self._isActive(interactable): continue
            if len(interactable["image_obj"]) > 0:
                if interactable["type"] == "SAVE_POINT":
                    interactable["timer"] -= 1
                    if interactable["timer"] <= 0:
                        interactable["frame_index"] += 1
                        if interactable["frame_index"] > len(interactable["image_obj"]) - 1:
                            interactable["frame_index"] = 0
                        interactable["timer"] = 5
                elif interactable["type"] == "NPC":
                    if interactable.get("is_speaking", False):
                        interactable["timer"] -= 1
                        if interactable["timer"] <= 0:
                            interactable["frame_index"] += 1
                            if interactable["frame_index"] > len(interactable["image_obj"]) - 1:
                                interactable["frame_index"] = 0
                            interactable["timer"] = 5
                    else:
                        if interactable.get("frame_index", 0) != 0:
                            interactable["frame_index"] = 0


    def draw(self, surface, camera):
        """Draws the new image positions on the surface."""
        surface.blit(self.bg_image, (0 - camera.x, 0 - camera.y))

        for interactable in self.interactables:
            if not self._isActive(interactable): continue

            if interactable.get("is_animated", False):
                current_image = interactable["image_obj"][interactable["frame_index"]]
            else:
                current_image = interactable["image_obj"]

            rect = current_image.get_rect(center=(interactable["x"] - camera.x, interactable["y"] - camera.y))
            surface.blit(current_image, rect)

        if self.debug_mode: self._draw_debug(surface, camera) # DEBUG MODE


    def _draw_debug(self, surface, camera):
        """Draws the debug rectangles/circles dynamically every frame."""
        def draw_rects(element_list, color, width=2):
            for element in element_list:
                if not self._isActive(element): continue
                
                if "x1" in element:
                    x1, y1 = element["x1"], element["y1"]
                    x2, y2 = element["x2"], element["y2"]
                
                else:
                    obj_x, obj_y = element["x"], element["y"]
                    if isinstance(element.get("image_obj"), list) and len(element["image_obj"]) > 0:
                        img = element["image_obj"][element.get("frame_index", 0)]
                    else:
                        img = element.get("image_obj")
                        
                    if img:
                        half_w = img.get_width() / 2
                        half_h = img.get_height() / 2
                    else:
                        half_w, half_h = 15, 15
                        
                    x1, y1 = obj_x - half_w, obj_y - half_h
                    x2, y2 = obj_x + half_w, obj_y + half_h

                rect = pygame.Rect(x1 - camera.x, y1 - camera.y, x2 - x1, y2 - y1)
                pygame.draw.rect(surface, color, rect, width)

        draw_rects(self.walls, "blue")
        draw_rects(self.exits, "red")
        draw_rects(self.triggers, "pink")
        draw_rects(self.interactables, "yellow")

        for spawn in self.spawns:
            cx = spawn["x"] - camera.x
            cy = spawn["y"] - camera.y
            pygame.draw.circle(surface, "green", (cx, cy), 20, width=2)


    def _isActive(self, interactable):
        """Checks if an interactable is currently active in the room."""
        if interactable.get("is_active", False): 
            return False
        
        if interactable.get("cutscene") is not None:
            if self.flags.get(f"cutscene_{interactable['cutscene']}_completed", False):
                return False

        return True