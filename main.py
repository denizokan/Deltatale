import tkinter
from PIL import Image, ImageTk
from src.core.constants import Constants
from src.core.enums import Action, GameState
from src.core.input import InputManager
from src.core.transition import TransitionManager
from src.core.player import Player
from src.screens.file_select import FileSelectScreen
from src.systems.savesystem import SaveSystem
from pygame import mixer

class Main:
    def __init__(self):
        """
        This function gets called when the game is first launched. 
        It handles window creation, key mappings, state initialization, 
        and starts the main execution thread.
        """

        root = tkinter.Tk()
        self.constants = Constants()
        root.title("Deltatale")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int((screen_width / 2) - (self.constants.WIDTH / 2))
        center_y = int((screen_height / 2) - (self.constants.HEIGHT / 2))
        root.geometry(f"{self.constants.WIDTH}x{self.constants.HEIGHT}+{center_x}+{center_y}")
        root.resizable(False, False)

        self.root = root

        self.canvas = tkinter.Canvas(root, width=self.constants.WIDTH, height=self.constants.HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack()

        # Initialize Managers
        self.input_manager = InputManager()
        mixer.init()
        self.save_system = SaveSystem()
        self.transition = TransitionManager(self)

        root.bind("<KeyPress>", self.input_manager.press_key)
        root.bind("<KeyRelease>", self.input_manager.release_key)

        # Load Sprites
        self.logo_sprite = tkinter.PhotoImage(file="assets/LOGO.png")
        self.player_sprite = tkinter.PhotoImage(file="sprites/SOUL.png")
        self.active_ui_elements = []

        self.current_room = None

        self.state = GameState.INTRO # Possible states: INTRO, FILE_SELECT, PLAYING, BATTLE, GAMEOVER
        self.setup_intro() # Enter the main menu

        self.game_loop() # Start the game loop
        root.mainloop()
    
    def clear_screen(self):
        """Helper to wipe out any UI elements from the previous state."""
        for element in self.active_ui_elements:
            self.canvas.delete(element)
        self.active_ui_elements.clear()

    def setup_intro(self):
        """Shows the Logo, instructions, and plays the introductory sound."""
        self.clear_screen()
        
        # Draw Logo
        pil_logo = Image.open("assets/LOGO.png")
        target_width = self.constants.WIDTH - 80
        scale_ratio = target_width / pil_logo.width
        target_height = int(pil_logo.height * scale_ratio)
        resized_logo = pil_logo.resize((target_width, target_height), Image.Resampling.NEAREST)
        self.logo_sprite = ImageTk.PhotoImage(resized_logo)
        logo = self.canvas.create_image(
            self.constants.WIDTH // 2, 
            self.constants.HEIGHT // 2.2, 
            image=self.logo_sprite
        )
        
        self.active_ui_elements.append(logo)

        intro_sound = mixer.Sound("sounds/undertale_sounds/mus_intronoise.ogg")
        intro_sound.set_volume(1)
        intro_sound.play()

        def show_text():
            # Only draw the text if the player hasn't skipped past the intro screen yet
            if self.state == GameState.INTRO:
                text = self.canvas.create_text(
                    self.constants.WIDTH // 2,
                    self.constants.HEIGHT // 2 + 120,
                    text="Press [Z] or [Enter]",
                    fill="gray",
                    justify="center",
                    font=("Determination Sans", 20, "normal")
                )
                self.active_ui_elements.append(text)

        self.root.after(3000, show_text)

    def setup_file_select(self):
        """Transition from intro to the separate File Selection class module."""
        self.clear_screen()
        self.state = GameState.FILE_SELECT
        self.file_select_screen = FileSelectScreen(self)

    def start_game(self, index):
        """Transition from file selection screen to the game."""
        # TODO: Get x, y from save index.
        self.player = Player(self, 300, 200, "right")
        
        self.file_select_screen = None
        self.state = GameState.PLAYING
        self.transition.fade_from_black(speed=8)
        

    def game_loop(self):
        # State: INTRO -> Waiting for confirm to go to File Select
        if self.state == GameState.INTRO:
            if self.input_manager.is_just_pressed(Action.CONFIRM):
                self.setup_file_select()

        # State: FILE_SELECT -> Waiting for confirm to start playing
        elif self.state == GameState.FILE_SELECT:
            self.file_select_screen.handle_input(input_mgr=self.input_manager)

        # State: PLAYING -> Handle player movement
        elif self.state == GameState.PLAYING:
            self.player.update(input_mgr=self.input_manager)

        self.input_manager.update()
        delay_ms = int(1000 / self.constants.FPS)
        self.root.after(delay_ms, self.game_loop)
    
if __name__ == "__main__":
    main = Main()