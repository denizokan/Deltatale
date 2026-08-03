import json
import pygame
from src.core.transition import TransitionManager
from src.core.camera import Camera
from src.core.player import Player
from src.core.room import Room
from src.core.events import EventBus
from src.core.constants import Constants, Color
from src.core.enums import Event, Interactable
from src.screens.save_screen import SaveScreen
from src.systems.cutscene_manager import CutsceneManager

class WorldManager:
    """Owns the player, the room, and the camera. Handles map logic."""
    def __init__(self, context, selected_file_index, save_data):
        self.context = context
        self.context.world = self
        self.selected_file_index = selected_file_index
        self.save_data = save_data

        self.asset_manager = self.context.assets
        self.transition_manager = self.context.transitions
        self.save_system = self.context.saves

        self.flags = self.context.flags
        self.last_save_time = pygame.time.get_ticks()

        self.save_screen = SaveScreen(self.asset_manager)
        self.camera = Camera()
        self.current_room = Room(save_data["room"], self.asset_manager, self.flags)
        self.cutscene_manager = CutsceneManager(self.context)

        spawn_info = None
        for interactable in self.current_room.interactables:
            if interactable["type"] == Interactable.SAVE_POINT.value:
                spawn_info = interactable["spawn_info"]
                break
        
        if spawn_info is None:
            # It's a brand new game
            spawn_x = 330
            spawn_y = 220
            spawn_facing = "down"
        else:
            # Spawn in front of the save point!
            spawn_x = spawn_info["spawn_x"]
            spawn_y = spawn_info["spawn_y"]
            spawn_facing = spawn_info["spawn_facing"]

        self.player = Player(spawn_x, spawn_y, spawn_facing, self.asset_manager)

        if hasattr(self.current_room, "music"):
            self.current_room.music.play(loops=-1)

        # Event Busses
        EventBus.subscribe(Event.CHANGE_ROOM, self.handle_room_switch)
        
        if spawn_info == None:
            EventBus.emit(Event.START_CUTSCENE, "first_room")
            return
    
        self.transition_manager.fade_from_black(speed=8)


    def update(self, input_manager, is_dialogue_active=False):
        if self.save_screen.is_active:
            self.save_screen.handle_input(input_manager)
            self.save_screen.update()
            
        elif not self.transition_manager.is_transitioning:
            if self.cutscene_manager.active_cutscene != None:
                self.cutscene_manager.update()

            is_cinematic = self.cutscene_manager.active_cutscene != None and self.cutscene_manager.blocks_player
            if not is_cinematic and not is_dialogue_active:
                self.player.update(input_manager, self.current_room)

            self.current_room.update()
            self.camera.update(self.player, self.current_room)


    def draw(self, surface, clock):
        self.current_room.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        self.cutscene_manager.draw(surface, self.camera)
        if self.current_room.debug_mode: self._draw_debug_text(surface, clock)
        
        if self.save_screen.is_active:
            self.save_screen.draw(surface)


    def open_save_menu(self, interactable):
        current_data = self.save_system.load_file(self.selected_file_index)
        
        def process_save(interactable_data):
            current_time = pygame.time.get_ticks()
            elapsed_ms = current_time - self.last_save_time
            elapsed_seconds = elapsed_ms // 1000

            current_data["location"] = interactable_data["location"]
            current_data["room"] = self.current_room.room_id
            current_data["flags"] = self.flags
            current_data["playtime"] += elapsed_seconds
            
            self.save_system.save_file(self.selected_file_index, current_data)
            
            self.save_data = current_data
            self.last_save_time = current_time - (elapsed_ms % 1000)
            return current_data

        self.save_screen.show_save_screen(current_data, interactable, process_save)


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

        next_room_data = self.asset_manager.get_room_data(target_room_id)
        if self.current_room.room_data["music"] != next_room_data["music"]:
            if hasattr(self.current_room, "music"):
                self.current_room.music.fadeout(500)

        self.transition_manager.fade_to_black(speed=24, on_complete=lambda: load_new_room(target_room_id))