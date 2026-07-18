from action import Action

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
            "Return": False
        }

    def press_key(self, event):
        """Callback for keyboard press."""
        if event.keysym in self.keys:
            self.keys[event.keysym] = True

    def release_key(self, event):
        """Callback for keyboard release."""
        if event.keysym in self.keys:
            self.keys[event.keysym] = False

    def is_pressed(self, action):
        """
        A helper function to group similar keys together.
        E.g., checking if "z" OR "Return" is pressed for confirmation.
        """
        if action == Action.CONFIRM:
            return self.keys["z"] or self.keys["Z"] or self.keys["Return"]
        if action == Action.CANCEL:
            return self.keys["x"] or self.keys["X"]
        if action == Action.MENU:
            return self.keys["c"] or self.keys["C"]
        
        if action == Action.UP:
            return self.keys["Up"]
        if action == Action.DOWN:
            return self.keys["Down"]
        if action == Action.LEFT:
            return self.keys["Left"]
        if action == Action.RIGHT:
            return self.keys["Right"]
        return False