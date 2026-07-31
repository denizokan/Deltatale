import json
from src.core.transition import TransitionManager
from src.core.camera import Camera
from src.core.player import Player
from src.core.room import Room
from src.core.events import EventBus
from src.core.constants import Constants, Color
from src.core.enums import Event

class WorldManager:
    """Owns the player, the room, and the camera. Handles map logic."""
    def __init__(self, asset_manager, selected_slot, flags):
        self.asset_manager = asset_manager
        self.selected_slot = selected_slot
        self.flags = flags
        
        self.transition_manager = TransitionManager()
        self.camera = Camera()
        self.player = Player(100, 100, "down", self.asset_manager)
        self.current_room = Room("room_ruins1", self.asset_manager, self.flags)
        if hasattr(self.current_room, "music"):
            self.current_room.music.play(loops=-1)

        EventBus.subscribe(Event.CHANGE_ROOM, self.handle_room_switch)


    def handle_room_switch(self, target_room_id):
        """Event Bus method: Handles transition and initializing a new room object."""
        def load_new_room(target_room_id):
            old_room = self.current_room
            self.current_room = Room(target_room_id, self.asset_manager, self.flags)
    
            spawn_x, spawn_y, spawn_facing = 0, 0, "right"
            for spawn in self.current_room.room_data["spawns"]:
                if spawn["from_room"] == old_room.room_id:
                    spawn_x = spawn["x"]
                    spawn_y = spawn["y"]
                    spawn_facing = spawn["facing"]
                    break
    
            self.player.x = spawn_x
            self.player.y = spawn_y
            self.player.facing = spawn_facing
            self.player.anim_frame = 0
            self.player.anim_timer = 0
            self.player.history = [(spawn_x, spawn_y, spawn_facing, 0)] * self.player.follow_delay
    
            self.camera.update(self.player, self.current_room)
    
            if old_room.room_data["music"] != self.current_room.room_data["music"]:
                if hasattr(self.current_room, "music"):
                    self.current_room.music.play(loops=-1)
    
            if old_room.debug_mode == True: # DEBUG MODE
                self.current_room.toggle_debug()
    
            self.transition_manager.fade_from_black(speed=24)

        try:
            with open(self.path + target_room_id + ".json", "r") as file:
                next_room_peek = json.load(file)
            
            if self.room_data["music"] != next_room_peek["music"]:
                if hasattr(self, "music"):
                    self.music.fadeout(500)
        except Exception as e:
            print(f"Warning: Could not read next room music: {e}")
        self.transition_manager.fade_to_black(speed=24, on_complete=lambda: load_new_room(target_room_id))


    def update(self, input_manager):
        if not self.transition_manager.is_transitioning:
            self.player.update(input_manager, self.current_room)
            self.current_room.update()
            self.camera.update(self.player, self.current_room)
        self.transition_manager.update()


    def draw(self, surface, clock):
        self.current_room.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        self.transition_manager.draw(surface)
        if self.current_room.debug_mode: self._draw_debug_text(surface, clock)


    def _draw_debug_text(self, screen, clock):
        """Draws debug information on the screen."""
        debug_font = self.asset_manager.get_font("dtm_sans_36")
        debug_surf = debug_font.render(f"DEBUG MODE", False, Color.WHITE)
        screen.blit(debug_surf, (10, 3))

        fps_font = self.asset_manager.get_font("dtm_sans_16")
        current_fps = int(clock.get_fps())
        fps_surf = fps_font.render(f"FPS: {current_fps}", False, Color.YELLOW)
        screen.blit(fps_surf, (10, 45))

        coord_font = self.asset_manager.get_font("dtm_sans_24")
        coord_surf = coord_font.render(f"{self.player.x:.2f}, {self.player.y:.2f}", False, Color.WHITE)
        screen.blit(coord_surf, (Constants.WIDTH - coord_surf.get_width() - 5, 3))