import pygame
import sys
from src.core.input import InputManager
from src.core.enums import Event
from src.core.constants import Constants, Color
from src.core.player import Player
from src.core.room import Room
from src.core.camera import Camera
from src.core.events import EventBus
from src.systems.dialogue_system import DialogueSystem
from src.systems.asset_manager import AssetManager

class Main:
    def __init__(self):
        """
        This function gets called when the game is first launched. 
        It handles window creation, key mappings, state initialization, 
        and starts the main execution thread.
        """

        pygame.init()

        self.screen = pygame.display.set_mode((Constants.WIDTH, Constants.HEIGHT))
        pygame.display.set_caption("Deltatale")
        self.clock = pygame.time.Clock()

        # Load Managers
        self.input_manager = InputManager()

        self.asset_manager = AssetManager()
        self.asset_manager.load_all()

        self.player = Player(100, 100, "down", self.asset_manager, self.input_manager)
        self.dialogue_system = DialogueSystem(self.asset_manager)
        self.current_room = Room("room_ruins1", self.asset_manager)
        self.camera = Camera()

        # Busses
        EventBus.subscribe(Event.START_DIALOGUE, self.handle_dialogue)

        self.running = True

        self.update()


    def update(self):
        """The main execution thread. Runs Constants.FPS times per second."""

        while self.running:
            # ==========================================
            # PHASE 1: INPUT
            # ==========================================
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN: self.input_manager.press_key(event)
                if event.type == pygame.KEYUP: self.input_manager.release_key(event)

            # ==========================================
            # PHASE 2: MATH & LOGIC (UPDATE)
            # ==========================================
            
            if self.dialogue_system.is_active: 
                self.dialogue_system.handle_input(self.input_manager)
                self.dialogue_system.update()
            
            else:
                self.player.update(input_mgr=self.input_manager, current_room=self.current_room)                
                self.current_room.update()

            self.camera.update(self.player, self.current_room)
            self.input_manager.update()

            # ==========================================
            # PHASE 3: RENDER (DRAW)
            # ==========================================
            
            self.screen.fill(Color.BLACK)

            self.current_room.draw(self.screen, self.camera)
            self.player.draw(self.screen, self.camera)
            self.dialogue_system.draw(self.screen)

            if self.current_room.debug_mode:
                self._draw_debug_text(self.screen)

            pygame.display.update()
            self.clock.tick(Constants.FPS)

        pygame.quit()
        sys.exit()


    def _draw_debug_text(self, screen):
        """Draws debug information on the screen."""
        debug_font = self.asset_manager.get_font("dtm_sans_36")
        debug_surf = debug_font.render(f"DEBUG MODE", False, Color.WHITE)
        screen.blit(debug_surf, (5, 15))

        fps_font = self.asset_manager.get_font("dtm_sans_16")
        current_fps = int(self.clock.get_fps())
        fps_surf = fps_font.render(f"FPS: {current_fps}", False, Color.YELLOW)
        screen.blit(fps_surf, (5, 40))

        coord_font = self.asset_manager.get_font("dtm_sans_24")
        coord_surf = coord_font.render(f"{self.player.x:.2f}, {self.player.y:.2f}", False, Color.WHITE)
        screen.blit(coord_surf, (Constants.WIDTH - coord_surf.get_width() - 5, 15))


    def handle_dialogue(self, data):
        """Event Bus method: Stars a new dialogue with the data given."""
        text = data.get("text")
        interaction_index = data.get("interaction_index", 0)
        interaction_type = data.get("type")
        interactable = data.get("interactable")
        actors = data.get("actors")

        on_complete_cb = None
        if interaction_type == "SAVE_POINT":
            on_complete_cb = lambda: self.save_screen.show_save_screen(interactable)

        self.dialogue_system.start_dialogue(
            text=text,
            interaction_index=interaction_index,
            actors=actors,
            on_complete=on_complete_cb
        )

            
if __name__ == "__main__":
    main = Main()