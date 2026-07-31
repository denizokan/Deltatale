import pygame
from src.core.constants import Constants, Color

class TransitionManager:
    """Handles smooth screen fade transitions."""
    def __init__(self):
        self.fade_alpha = 0
        self.speed = 0
        self.target_alpha = 0
        self.is_transitioning = False
        self.on_complete_callback = None

        self.fade_surface = pygame.Surface((Constants.WIDTH, Constants.HEIGHT))
        self.fade_surface.fill(Color.BLACK)


    def fade_to_black(self, speed=8, on_complete=None):
        """Starts a transition to a fully black screen."""
        if self.is_transitioning: return
        self.is_transitioning = True
        self.fade_alpha = 0
        self.target_alpha = 255
        self.speed = speed
        self.on_complete_callback = on_complete


    def fade_from_black(self, speed=8, on_complete=None):
        """Starts a transition from a black screen to fully transparent."""
        if self.is_transitioning: return
        self.is_transitioning = True
        self.fade_alpha = 255
        self.target_alpha = 0
        self.speed = -speed
        self.on_complete_callback = on_complete


    def update(self):
        """Updates the alpha transparency. Must be called in the main loop."""
        if not self.is_transitioning: return

        self.fade_alpha += self.speed

        reached_target = False
        if self.speed > 0 and self.fade_alpha >= self.target_alpha:
            self.fade_alpha = self.target_alpha
            reached_target = True
        elif self.speed < 0 and self.fade_alpha <= self.target_alpha:
            self.fade_alpha = self.target_alpha
            reached_target = True

        if reached_target:
            self.is_transitioning = False
            
            if self.on_complete_callback:
                cb = self.on_complete_callback
                self.on_complete_callback = None
                cb()


    def draw(self, surface):
        """Draws the fade overlay. Must be called LAST in the render phase."""
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(self.fade_surface, (0, 0))