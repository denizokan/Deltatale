from src.core.enums import Action

class InputManager:
    """
    Class for checking inputs.
    """

    def __init__(self):
        self.keys = {
            "Left": False, "Right": False, "Up": False, "Down": False,
            "z": False, "Z": False,
            "x": False, "X": False,
            "c": False, "C": False,
            "Return": False,
            "udiaeresis": False, "Udiaeresis": False # Debug keys (ü, Ü)
        }
        self.pressed_this_frame = {k: False for k in self.keys}
        self.action_stack = []


    def press_key(self, event):
        """Callback for keyboard press."""
        if event.keysym in self.keys:
            if not self.keys[event.keysym]:
                self.pressed_this_frame[event.keysym] = True
            self.keys[event.keysym] = True

        if event.keysym in ["Up", "Down", "Left", "Right"]:
            if not event.keysym in self.action_stack:
                self.action_stack.append(event.keysym)


    def release_key(self, event):
        """Callback for keyboard release."""
        if event.keysym in self.keys:
            self.keys[event.keysym] = False
            self.pressed_this_frame[event.keysym] = False

        if event.keysym in self.action_stack:
            self.action_stack.remove(event.keysym)

    
    def get_active_direction(self):
        if len(self.action_stack) != 0:
            return self.action_stack[-1]
        return None


    def is_pressed(self, action):
        """Checks if a key is being held down continuously (Good for Movement)."""
        if action == Action.CANCEL:    return self.keys["x"] or self.keys["X"]
        if action == Action.UP:        return self.keys["Up"]
        if action == Action.DOWN:      return self.keys["Down"]
        if action == Action.LEFT:      return self.keys["Left"]
        if action == Action.RIGHT:     return self.keys["Right"]
        return False


    def is_just_pressed(self, action):
        """Checks if a button was freshly tapped on this frame (Good for Menus)."""
        if action == Action.CONFIRM:
            return self.pressed_this_frame["z"] or self.pressed_this_frame["Z"] or self.pressed_this_frame["Return"]
        if action == Action.CANCEL:
            return self.pressed_this_frame["x"] or self.pressed_this_frame["X"]
        if action == Action.MENU:
            return self.pressed_this_frame["c"] or self.pressed_this_frame["C"]
        
        if action == Action.UP:
            return self.pressed_this_frame["Up"]
        if action == Action.DOWN:
            return self.pressed_this_frame["Down"]
        if action == Action.LEFT:
            return self.pressed_this_frame["Left"]
        if action == Action.RIGHT:
            return self.pressed_this_frame["Right"]

        if action == Action.DEBUG: # Debug key check
            return self.pressed_this_frame["udiaeresis"] or self.pressed_this_frame["Udiaeresis"]

        return False


    def update(self):
        """Clears out the single-press triggers. MUST be called at the end of every frame loop."""
        for key in self.pressed_this_frame:
            self.pressed_this_frame[key] = False