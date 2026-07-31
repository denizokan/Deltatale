import pygame
from src.core.enums import Action

class InputManager:
    """
    Class for checking inputs.
    """

    def __init__(self):
        self.keys = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False,
            pygame.K_z: False,
            pygame.K_x: False,
            pygame.K_c: False,
            pygame.K_RETURN: False,
            pygame.K_ESCAPE: False,
            pygame.K_COMMA: False # Debug key (,)
        }
        self.pressed_this_frame = {k: False for k in self.keys}
        self.action_stack = []


    def press_key(self, event):
        """Callback for keyboard press."""
        if event.key in self.keys:
            if not self.keys[event.key]:
                self.pressed_this_frame[event.key] = True
            self.keys[event.key] = True

        if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
            if not event.key in self.action_stack:
                self.action_stack.append(event.key)


    def release_key(self, event):
        """Callback for keyboard release."""
        if event.key in self.keys:
            self.keys[event.key] = False
            self.pressed_this_frame[event.key] = False

        if event.key in self.action_stack:
            self.action_stack.remove(event.key)

    
    def get_active_direction(self):
        if len(self.action_stack) != 0:
            return self.action_stack[-1]
        return None


    def is_pressed(self, action):
        """Checks if a key is being held down continuously (Good for Movement)."""
        if action == Action.QUIT:      return self.keys[pygame.K_ESCAPE]
        if action == Action.CANCEL:    return self.keys[pygame.K_x]
        if action == Action.UP:        return self.keys[pygame.K_UP]
        if action == Action.DOWN:      return self.keys[pygame.K_DOWN]
        if action == Action.LEFT:      return self.keys[pygame.K_LEFT]
        if action == Action.RIGHT:     return self.keys[pygame.K_RIGHT]
        return False


    def is_just_pressed(self, action):
        """Checks if a button was freshly tapped on this frame (Good for Menus)."""
        if action == Action.CONFIRM:
            return self.pressed_this_frame[pygame.K_z] or self.pressed_this_frame[pygame.K_RETURN]
        if action == Action.CANCEL:
            return self.pressed_this_frame[pygame.K_x]
        if action == Action.MENU:
            return self.pressed_this_frame[pygame.K_c]
        
        if action == Action.UP:
            return self.pressed_this_frame[pygame.K_UP]
        if action == Action.DOWN:
            return self.pressed_this_frame[pygame.K_DOWN]
        if action == Action.LEFT:
            return self.pressed_this_frame[pygame.K_LEFT]
        if action == Action.RIGHT:
            return self.pressed_this_frame[pygame.K_RIGHT]

        if action == Action.QUIT:
            return self.pressed_this_frame[pygame.K_ESCAPE]
        if action == Action.DEBUG: # Debug key check
            return self.pressed_this_frame[pygame.K_COMMA]

        return False


    def update(self):
        """Clears out the single-press triggers. MUST be called at the end of every frame loop."""
        for key in self.pressed_this_frame:
            self.pressed_this_frame[key] = False