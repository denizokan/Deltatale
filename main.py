import tkinter
from constants import Constants

# Constants
constants = Constants()

class Main:
    def __init__(self):
        """
        This function gets called when the game is first launched. 
        It handles window creation, key mappings, state initialization, 
        and starts the main execution thread.
        """

        root = tkinter.Tk()
        root.title("Undertale Blue")
        root.geometry(f"{constants.WIDTH}x{constants.HEIGHT}")
        root.resizable(False, False)

        self.root = root

        self.canvas = tkinter.Canvas(root, width=constants.WIDTH, height=constants.HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack()

        self.keys = {
            "Left": False, "Right": False, "Up": False, "Down": False,
            "z": False, "Z": False,
            "x": False, "X": False,
            "c": False, "C": False,
            "Return": False
        }

        root.bind("<KeyPress>", self.press_key)
        root.bind("<KeyRelease>", self.release_key)

        self.state = "MENU" # Possible states: MENU, PLAYING, BATTLE, GAMEOVER

        self.setup_menu() # Enter the main menu
        self.game_loop() # Start the game loop

        root.mainloop()

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
        if action == "confirm":
            return self.keys["z"] or self.keys["Z"] or self.keys["Return"]
        if action == "cancel":
            return self.keys["x"] or self.keys["X"]
        if action == "menu":
            return self.keys["c"] or self.keys["C"]
        return False

    def setup_menu(self):
        """Draws the initial main menu layout on the canvas."""
        self.menu_text = self.canvas.create_text(
            constants.WIDTH // 2,
            constants.HEIGHT // 2,
            text="UNDERTALE Blue\n\nPress [Z] or [Enter] to start.",
            fill="white",
            justify="center",
            font=("Determination Sans", 26, "normal")
        )

    def start_game(self):
        """Transition from menu to active gameplay."""
        self.canvas.delete(self.menu_text)
        self.state = "PLAYING"

        self.player_x = constants.WIDTH // 2
        self.player_y = constants.HEIGHT - 80
        self.player = self.canvas.create_rectangle(
            self.player_x - 8, self.player_y - 8, 
            self.player_x + 8, self.player_y + 8, 
            fill="blue", outline=""
        )

    def game_loop(self):
        if self.state == "MENU":
            if self.is_pressed("confirm"):
                self.start_game()

        elif self.state == "PLAYING":
            dx = 0
            if self.keys["Left"]:
                dx = -4
            if self.keys["Right"]:
                dx = 4
                
            if dx != 0:
                self.canvas.move(self.player, dx, 0)

        delay_ms = int(1000 / constants.FPS)
        self.root.after(delay_ms, self.game_loop)
    
if __name__ == "__main__":
    main = Main()