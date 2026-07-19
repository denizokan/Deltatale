from pygame import mixer
from action import Action

class FileSelectScreen:
    """
    This class handles file selection, loading, copying and deleting.    
    """

    def __init__(self, main_game):
        """
        Initializes the file selection screen.
        
        Parameters:
            main_game (Main): A reference to the main application class instance,
                            allowing access to the Canvas, Constants, and InputManager.
        """
        self.game = main_game
        self.menu_index = 0
        self.active_ui_elements = []
        self.ui_positions = []
        
        self.setup_layout()

    def setup_layout(self):
        """
        Constructs the screen layout by rendering background music, text prompts, 
        the three file selection boxes with save status information, the action 
        buttons, and initializing the SOUL cursor asset.

        Docs:
        ```
        self.game.canvas.create_text(
            x,                       # (int/float) X pixel coordinate on the grid
            y,                       # (int/float) Y pixel coordinate on the grid
            text="Your Text Here",   # (string) The actual text to display
            fill="white",            # (string) The text color ("white", "gray", "red", etc.)
            font=("Font Name", 20),  # (tuple) (Font Family, Size, "bold"/"normal")
            anchor="w",              # (string) Text alignment origin: "w" (left), "e" (right), "center"
            justify="center"         # (string) Multi-line text alignment ("left", "center", "right")
        )
        ```
        """
        
        sound = mixer.Sound(file="sounds/menu_theme.mp3")
        sound.play(loops=-1)

        title_text = self.game.canvas.create_text(
            90,
            65,
            text="Please select a file.",
            fill="white",
            font=("Determination Sans", 24, "normal"),
            anchor="w"
        )
        self.active_ui_elements.append(title_text)

        # --- Box Variables ---
        box_width = self.game.constants.WIDTH // 1.7
        box_height = 85
        start_y = 100
        spacing = 95

        save_slots = [
            {"name": "[EMPTY]", "location": "------", "time": "--:--", "isEmpty": True},
            {"name": "[EMPTY]", "location": "------", "time": "--:--", "isEmpty": True},
            {"name": "[EMPTY]", "location": "------", "time": "--:--", "isEmpty": True}
        ]

        # Create the save slot boxes & their texts
        self.slot_visual_ids = []
        
        for index, slot in enumerate(save_slots):
            x1 = (self.game.constants.WIDTH - box_width) // 2
            x2 = x1 + box_width
            y1 = start_y + (index * spacing)
            y2 = y1 + box_height

            self.ui_positions.append((x1, y1, x2, y2))
            save_slot_box = self.game.canvas.create_rectangle(x1, y1, x2, y2, outline="gray", width=2)
            self.active_ui_elements.append(save_slot_box)

            name_text = self.game.canvas.create_text(
                x1 + 60,
                y1 + 25,
                text=f"{slot['name']}",
                fill="gray",
                font=("Determination Sans", 24, "normal"),
                anchor="w"
            )
            location_text = self.game.canvas.create_text(
                x1 + 60,
                y1 + 60,
                text=f"{slot['location']}",
                fill="gray",
                font=("Determination Sans", 24, "normal"),
                anchor="w"
            )
            time_text = self.game.canvas.create_text(
                x2 - 60,
                y1 + 25,
                text=f"{slot['time']}",
                fill="gray",
                font=("Determination Sans", 24, "normal"),
                anchor="e"
            )

            self.active_ui_elements.extend([name_text, location_text, time_text])
            self.slot_visual_ids.append({
                "box": save_slot_box,
                "name": name_text,
                "location": location_text,
                "time": time_text
            })

        # Copy, Erase, Quit Buttons
        start_x = (self.game.constants.WIDTH - box_width) // 2
        btn_y = 410

        self.button_positions = [
            (start_x + 25, btn_y, "Copy"),
            (self.game.constants.WIDTH // 2, btn_y, "Erase"),
            (start_x + box_width - 25, btn_y, "Quit")
        ]

        self.button_visual_ids = []

        for index, button in enumerate(self.button_positions):
            button_text = self.game.canvas.create_text(
                button[0],
                button[1],
                text=button[2],
                fill="gray",
                font=("Determination Sans", 24, "normal"),
                anchor="center"
            )
            self.active_ui_elements.append(button_text)
            self.button_visual_ids.append(button_text)

        # Footer text
        footer_text = self.game.canvas.create_text(
            self.game.constants.WIDTH - 5,
            self.game.constants.HEIGHT - 15,
            text="DELTATALE 0.0.1",
            fill="gray",
            font=("Determination Sans", 16, "normal"),
            anchor="e"
        )
        self.active_ui_elements.append(footer_text)

        # Create the soul/selector sprite
        self.menu_soul = self.game.canvas.create_image(0, 0, image=self.game.player_sprite)
        self.active_ui_elements.append(self.menu_soul)
        
        self.update_visuals()

    def update_visuals(self):
        """
        Calculates the exact screen coordinates for the SOUL cursor based on the 
        current menu_index state, then moves the canvas image component to match.
        """
        box_height = 85

        if self.menu_index <= 2: # Highlighting save box
            coords = self.ui_positions[self.menu_index]
            target_x = coords[0] + 30
            target_y = coords[1] + box_height // 2

        else: # Player is highlighting menu buttons
            i = self.menu_index - 3 # Menu button index (0: Copy, 1: Erase, 2: Quit)
            button_info = self.button_positions[i]
            target_x = self.game.canvas.bbox(self.button_visual_ids[i])[0] - 20
            target_y = button_info[1]

        self.game.canvas.coords(self.menu_soul, target_x, target_y)

        for index, slot in enumerate(self.slot_visual_ids):
            if self.menu_index == index:
                self.game.canvas.itemconfig(slot['box'], outline="white")
                self.game.canvas.itemconfig(slot['name'], fill="white")
                self.game.canvas.itemconfig(slot['location'], fill="white")
                self.game.canvas.itemconfig(slot['time'], fill="white")
            else:
                self.game.canvas.itemconfig(slot['box'], outline="gray")
                self.game.canvas.itemconfig(slot['name'], fill="gray")
                self.game.canvas.itemconfig(slot['location'], fill="gray")
                self.game.canvas.itemconfig(slot['time'], fill="gray")
        for index, button in enumerate(self.button_visual_ids):
            if self.menu_index == index + 3:
                self.game.canvas.itemconfig(button, fill="white")
            else:
                self.game.canvas.itemconfig(button, fill="gray")

    def handle_input(self):
        input_mgr = self.game.input_manager
        moved = False

        if input_mgr.is_just_pressed(Action.UP):
            if self.menu_index >= 3:
                self.menu_index = 2
                moved = True
            elif self.menu_index > 0:
                self.menu_index -= 1
                moved = True

        if input_mgr.is_just_pressed(Action.DOWN):
            if self.menu_index >= 3:
                pass
            else:
                self.menu_index += 1
                moved = True

        if input_mgr.is_just_pressed(Action.LEFT):
            if self.menu_index > 3:
                self.menu_index -= 1
                moved = True
        
        if input_mgr.is_just_pressed(Action.RIGHT):
            if 3 <= self.menu_index < 5:
                self.menu_index += 1
                moved = True

        if moved:
            sound = mixer.Sound(file="sounds/undertale_sounds/snd_squeak.wav")
            sound.play()
            self.update_visuals()