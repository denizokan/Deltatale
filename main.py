import tkinter
from tkinter import messagebox
from PIL import Image, ImageTk
from src.core.constants import Constants
from src.core.enums import Action, GameState, Interactable
from src.core.input import InputManager
from src.core.transition import TransitionManager
from src.core.player import Player
from src.core.room import Room
from src.core.camera import Camera
from src.screens.menu_screen import MenuScreen
from src.screens.save_screen import SaveScreen
from src.screens.file_select import FileSelectScreen
from src.systems.save_system import SaveSystem
from src.systems.dialogue_system import DialogueSystem
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
        self.save_screen = SaveScreen(self)
        self.menu_screen = MenuScreen(self)
        self.transition = TransitionManager(self)
        self.dialogue_system = DialogueSystem(self)

        root.bind("<KeyPress>", self.input_manager.press_key)
        root.bind("<KeyRelease>", self.input_manager.release_key)

        self.quit_hold_timer = 0
        self.quit_text_id = None
        self.MAX_QUIT_TICKS = 45
        self.playtime_ticks = 30
        self.playtime = 0

        # Load Sprites
        self.logo_sprite = tkinter.PhotoImage(file="assets/LOGO.png")
        self.player_sprite = tkinter.PhotoImage(file="sprites/SOUL.png")
        self.active_ui_elements = []

        self.current_room = None
        self.selected_file_index = None

        self.state = GameState.INTRO # Possible states: INTRO, FILE_SELECT, PLAYING, CUTSCENE, BATTLE, GAMEOVER
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
        if not self.save_system.exists(index):
            data = self.save_system.create_blank_save()
            try:
                self.save_system.save_file(index, data)
            except RuntimeError as e:
                self.root.destroy()
                messagebox.showerror(
                    "An error has occured.",
                    f"{e}"
                )
                exit(1)

        self.selected_file_index = index
        
        data = self.save_system.load_file(index)
        self.camera = Camera(self)
        self.current_room = Room(self, data["room"])

        spawn_info = None
        for interactable in self.current_room.interactables:
            if interactable["type"] == Interactable.SAVE_POINT.value:
                spawn_info = interactable["spawn_info"]
                break

        if spawn_info is None:
            # It's a room without a save point, or a brand new game!
            spawn_x = 320
            spawn_y = 240
            spawn_facing = "down"
        else:
            # Spawn in front of the save point!
            spawn_x = spawn_info["spawn_x"]
            spawn_y = spawn_info["spawn_y"]
            spawn_facing = spawn_info["spawn_facing"]

        self.player = Player(self, spawn_x, spawn_y, spawn_facing)
        self.camera.update()
        self.player.draw(spawn_x, spawn_y, spawn_facing, 0)

        for character in self.player.active_characters:
            self.canvas.tag_raise(character)

        if spawn_facing == "down":
            self.canvas.tag_raise(self.player.active_characters[0]) # Put Kris at top
        if spawn_facing == "up":
            self.canvas.tag_raise(self.player.active_characters[0]) # Put Susie at top
        
        self.file_select_screen = None
        self.state = GameState.PLAYING

        if hasattr(self.current_room, "music"):
            self.root.after(1000, lambda: self.current_room.music.play(loops=-1))

        self.transition.fade_from_black(speed=24)
        

    def game_loop(self):
        self.handle_quit() # Listen for quit inputs

        # State: INTRO -> Waiting for confirm to go to File Select
        if self.state == GameState.INTRO:
            if self.input_manager.is_just_pressed(Action.CONFIRM):
                self.setup_file_select()

        # State: FILE_SELECT -> Waiting for confirm to start playing
        elif self.state == GameState.FILE_SELECT:
            self.file_select_screen.handle_input(input_mgr=self.input_manager)

        # State: PLAYING -> Handle player movement
        elif self.state == GameState.PLAYING:
            self.update_playtime()

            if self.cutscene_manager.is_active:
                self.cutscene_manager.update()
            
            if self.dialogue_system.is_active: # If dialogue is active
                self.dialogue_system.handle_input(self.input_manager)
                self.dialogue_system.update()

            elif self.save_screen.is_active: # If save screen is active
                self.save_screen.handle_input(self.input_manager)

            elif self.menu_screen.is_active:
                self.menu_screen.handle_input(self.input_manager)

            else:
                is_cinematic = self.cutscene_manager.is_active and self.cutscene_manager.blocks_player
                if not is_cinematic:
                    self.player.update(input_mgr=self.input_manager)
                    
                self.camera.update()
                self.canvas.coords(self.current_room.background, -self.camera.x, -self.camera.y)

                # Debug mode:
                if self.input_manager.is_just_pressed(Action.DEBUG):
                    self.current_room.toggle_debug()
            self.current_room.update_positions()

        self.input_manager.update()
        delay_ms = int(1000 / self.constants.FPS)
        self.root.after(delay_ms, self.game_loop)


    def update_playtime(self):
        """Adds 1 to playtime every 30 game ticks while player is playing."""
        self.playtime_ticks -= 1
        if self.playtime_ticks <= 0:
            self.playtime += 1
            self.playtime_ticks = 30


    def handle_quit(self):
        """Handles ESC key press."""
        if self.input_manager.is_pressed(Action.QUIT):
            self.quit_hold_timer += 1

            FADE_TICKS = 15.0
            fade_progress = min(1.0, self.quit_hold_timer / FADE_TICKS)
            current_color = self.get_fade_color(fade_progress)

            dot_count = min(3, self.quit_hold_timer // 12)
            display_str = f"QUITTING{'.' * dot_count}"

            if self.quit_text_id is None:
                self.quit_text_id = self.canvas.create_text(
                    10, 20, 
                    text=display_str, 
                    fill=current_color, 
                    font=("Determination Sans", 24), 
                    anchor="w"
                )
            else:
                self.canvas.itemconfig(
                    self.quit_text_id, 
                    text=display_str, 
                    fill=current_color
                )

            if self.quit_hold_timer >= self.MAX_QUIT_TICKS:
                self.root.destroy()
                exit()

        else:
            if self.quit_hold_timer > 0:
                self.quit_hold_timer = 0
                if self.quit_text_id is not None:
                    self.canvas.delete(self.quit_text_id)
                    self.quit_text_id = None


    def get_fade_color(self, progress):
        """
        Returns a hex gray color based on progress (0.0 = black, 1.0 = white).
        """
        progress = max(0.0, min(1.0, progress))
        val = int(255 * progress)
        return f"#{val:02x}{val:02x}{val:02x}"
    

if __name__ == "__main__":
    main = Main()