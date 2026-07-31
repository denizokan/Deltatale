import pygame
import sys
from src.core.input import InputManager
from src.core.constants import Constants, Color
from src.core.player import Player
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

        self.running = True

        self.update()


    def update(self):
        """The main execution thread. Runs Constants.FPS times per second."""

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN: self.input_manager.press_key(event)
                if event.type == pygame.KEYUP: self.input_manager.release_key(event)

            self.screen.fill(Color.BLACK)

            player_signal = self.player.update(input_mgr=self.input_manager, current_room=self.current_room)
            if player_signal == "MENU":
                self.menu_screen.open_menu(index=0)

            self.player.draw(self.screen, self.camera)
            self.input_manager.update()

            pygame.display.update()
            self.clock.tick(Constants.FPS)

        pygame.quit()
        sys.exit()

            
if __name__ == "__main__":
    main = Main()