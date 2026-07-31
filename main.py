import pygame
import sys
from src.core.input import InputManager
from src.core.enums import Event, GameState
from src.core.constants import Constants, Color
from src.core.events import EventBus
from src.systems.world_manager import WorldManager
from src.systems.dialogue_system import DialogueSystem
from src.systems.asset_manager import AssetManager
from src.systems.save_system import SaveSystem
from src.core.transition import TransitionManager
from src.screens.intro_screen import IntroScreen
from src.screens.file_select import FileSelectScreen

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

        self.selected_file_index = 0
        self.flags = {}

        # Load Managers
        self.input_manager = InputManager()
        self.asset_manager = AssetManager()
        self.asset_manager.load_all()
        self.transition_manager = TransitionManager()
        self.save_system = SaveSystem()
        self.dialogue_system = DialogueSystem(self.asset_manager)

        # Busses
        EventBus.subscribe(Event.SWITCH_TO_FILE_SELECT, self.setup_file_select)
        EventBus.subscribe(Event.START_GAME, self.start_game)
        EventBus.subscribe(Event.START_DIALOGUE, self.handle_dialogue)

        self.state = GameState.INTRO
        self.running = True

        self.intro_screen = IntroScreen(self.asset_manager)
        self.game_loop()


    def game_loop(self):
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

            if not self.transition_manager.is_transitioning:

                if self.state == GameState.INTRO:
                    self.intro_screen.handle_input(self.input_manager)
                    if self.state == GameState.INTRO: self.intro_screen.update()
                elif self.state == GameState.FILE_SELECT:
                    self.file_select_screen.handle_input(self.input_manager)
                    if self.state == GameState.FILE_SELECT: self.file_select_screen.update_visuals()
                elif self.state == GameState.PLAYING:
                    if self.dialogue_system.is_active:
                        self.dialogue_system.handle_input(self.input_manager)
                        self.dialogue_system.update()
                        self.world_manager.current_room.update()
                    else:
                        self.world_manager.update(self.input_manager)

            self.transition_manager.update()
            self.input_manager.update()

            # ==========================================
            # PHASE 3: RENDER (DRAW)
            # ==========================================
            
            self.screen.fill(Color.BLACK)

            if self.state == GameState.INTRO:
                self.intro_screen.draw(self.screen)
            elif self.state == GameState.FILE_SELECT:
                self.file_select_screen.draw(self.screen)
            elif self.state == GameState.PLAYING:
                self.world_manager.draw(self.screen, self.clock)
                self.dialogue_system.draw(self.screen)

            self.transition_manager.draw(self.screen)

            pygame.display.update()
            self.clock.tick(Constants.FPS)

        pygame.quit()
        sys.exit()


    def setup_file_select(self, bool):
        """Event Bus method: Setups the file selection screen."""
        self.state = GameState.FILE_SELECT
        self.file_select_screen = FileSelectScreen(self.asset_manager, self.save_system)
        self.intro_screen = None


    def start_game(self, selected_slot):
        """Event Bus method: Starts the world manager."""
        def _start_world_manager(selected_slot):
            if not self.save_system.exists(selected_slot):
                data = self.save_system.create_blank_save()
                try:
                    self.save_system.save_file(selected_slot, data)
                except RuntimeError as e:
                    print(f"An error has occured: {e}")
                    pygame.quit()
                    sys.exit()

            data = self.save_system.load_file(selected_slot)
            self.state = GameState.PLAYING
            self.world_manager = WorldManager(self.asset_manager, self.transition_manager, data)
            self.world_manager.camera.update(self.world_manager.player, self.world_manager.current_room)
            self.world_manager.player.draw(self.screen, self.world_manager.camera)
            self.file_select_screen = None

        self.transition_manager.fade_to_black(8, on_complete=lambda: _start_world_manager(selected_slot))


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