import pygame
import sys
from src.core.input import InputManager
from src.core.constants import Constants, Color
from src.core.player import Player
from src.core.room import Room
from src.core.camera import Camera
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
        self.current_room = Room("room_ruins1", self.asset_manager, self.dialogue_system)
        self.camera = Camera()

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
                player_signal = self.player.update(input_mgr=self.input_manager, current_room=self.current_room)
                if player_signal == "MENU":
                    self.menu_screen.open_menu(index=0)
                
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

            pygame.display.update()
            self.clock.tick(Constants.FPS)

        pygame.quit()
        sys.exit()

            
if __name__ == "__main__":
    main = Main()