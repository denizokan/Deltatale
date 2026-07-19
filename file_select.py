from pygame import mixer

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
        
        sound = mixer.Sound(file="sounds/assets/menu_theme.mp3")
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
        for index, slot in enumerate(save_slots):
            x1 = (self.game.constants.WIDTH - box_width) // 2
            x2 = x1 + box_width
            y1 = start_y + (index * spacing)
            y2 = y1 + box_height

            self.ui_positions.append((x1, x2, y1, y2))
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

        # Copy, Erase, Quit Buttons
        start_x = (self.game.constants.WIDTH - box_width) // 2
        btn_y = 410

        self.button_positions = [
            (start_x + 25, btn_y, "Copy"),
            (self.game.constants.WIDTH // 2, btn_y, "Erase"),
            (start_x + box_width - 25, btn_y, "Quit")
        ]

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

        