import tkinter
from constants import Constants
from action import Action
from gamestate import GameState
from input_manager import InputManager
from pygame import mixer

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

        # Initialize Managers
        self.input_manager = InputManager()
        mixer.init()

        root.bind("<KeyPress>", self.input_manager.press_key)
        root.bind("<KeyRelease>", self.input_manager.release_key)

        self.state = GameState.MENU # Possible states: MENU, PLAYING, BATTLE, GAMEOVER

        self.setup_menu() # Enter the main menu
        self.game_loop() # Start the game loop

        root.mainloop()

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
        sound = mixer.Sound("assets/menu_theme.mp3")
        sound.play(loops=-1)

    def start_game(self):
        """Transition from menu to active gameplay."""
        self.canvas.delete(self.menu_text)
        self.state = GameState.PLAYING

        self.player_x = constants.WIDTH // 2
        self.player_y = constants.HEIGHT - 80
        self.player = self.canvas.create_rectangle(
            self.player_x - 8, self.player_y - 8, 
            self.player_x + 8, self.player_y + 8, 
            fill="blue", outline=""
        )

    def game_loop(self):
        if self.state == GameState.MENU:
            if self.input_manager.is_pressed(Action.CONFIRM):
                self.start_game()

        elif self.state == GameState.PLAYING:
            dx = 0
            dy = 0

            if self.input_manager.is_pressed(Action.UP):
                dy = -constants.SOUL_SPEED
            if self.input_manager.is_pressed(Action.DOWN):
                dy = constants.SOUL_SPEED
            if self.input_manager.is_pressed(Action.LEFT):
                dx = -constants.SOUL_SPEED
            if self.input_manager.is_pressed(Action.RIGHT):
                dx = constants.SOUL_SPEED
                
            if (dx != 0 or dy != 0):
                self.canvas.move(self.player, dx, dy)

        delay_ms = int(1000 / constants.FPS)
        self.root.after(delay_ms, self.game_loop)
    
if __name__ == "__main__":
    main = Main()