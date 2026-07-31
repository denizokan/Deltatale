import pygame
import sys
from src.core.constants import Constants, Color

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

        self.running = True

        self.update()


    def update(self):
        """The main execution thread. Runs Constants.FPS times per second."""

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False

            self.screen.fill(Color.BLACK)
            pygame.display.update()

            self.clock.tick(Constants.FPS)

        pygame.quit()
        sys.exit()
            


if __name__ == "__main__":
    main = Main()