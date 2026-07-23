from tkinter import messagebox
from pygame import mixer

class MenuScreen:
    """The menu gets triggered if the player presses the [C] key."""

    def __init__(self, main_game):
        self.game = main_game
        self.margin = 32

        self.is_active = False
        self.menu_index = 0
        self.layer_index = 0

        self.active_ui_elements = []


    def open_menu(self, index=0):
        """Opens the menu with given index."""
        self.is_active = True

        self._draw_main_boxes(index=0)
        self._draw_menu_text()


    def close_menu(self, index=0):
        """Closes the menu with given index. If index is 0, everything is closed."""
        pass


    def handle_input(self, input_mgr):
        """Handles keyboard inputs while a menu is open."""
        pass


    def update_visuals(self):
        """Updates selection regarding to keypresses."""
        pass


    def _draw_main_boxes(self, index):
        """Calculates and draws the core 3-box layout of the menu."""
        # Stats Box
        self.stats_x1 = self.margin
        self.stats_y1 = self.margin
        self.stats_x2 = self.margin + 150
        self.stats_y2 = self.margin + 120
        
        stats_box = self.game.canvas.create_rectangle(
            self.stats_x1, self.stats_y1, self.stats_x2, self.stats_y2,
            fill="black", outline="white", width=6
        )
        self.active_ui_elements.append(stats_box)

        # Action Box
        self.action_x1 = self.margin
        self.action_y1 = self.stats_y2 + 15
        self.action_x2 = self.stats_x2
        self.action_y2 = self.action_y1 + 180
        
        action_box = self.game.canvas.create_rectangle(
            self.action_x1, self.action_y1, self.action_x2, self.action_y2,
            fill="black", outline="white", width=6
        )
        self.active_ui_elements.append(action_box)

        if index >= 1:
            # Main Display Box
            self.main_x1 = self.stats_x2 + 15
            self.main_y1 = self.margin
            self.main_x2 = self.game.constants.WIDTH - self.margin
            self.main_y2 = self.game.constants.HEIGHT - self.margin
            
            self.main_box = self.game.canvas.create_rectangle(
                self.main_x1, self.main_y1, self.main_x2, self.main_y2,
                fill="black", outline="white", width=6
            )
            self.active_ui_elements.append(self.main_box)


    def _draw_menu_text(self):
        """Draws the small stats box text, menu option buttons, and the soul."""
        try:
            data = self.game.save_system.load_file(self.game.selected_file_index)
        except RuntimeError as e:
            self.game.root.destroy()
            messagebox.showerror(
                "An error has occured.",
                f"{e}"
            )
            exit(1)

        stats = [ # Level, HP, Money
            self.game.player.level, f"{self.game.player.hp}/", self.game.player.money
        ]

        name_text = self.game.canvas.create_text(
            self.margin + 10, self.margin + 10,
            text=data["name"],
            fill="white",
            font=("Determination Mono", 24, "normal"),
            anchor="w"
        )
        self.active_ui_elements.append(name_text)

        for index, item in enumerate(["LV", "HP", "G"]):
            text = self.game.canvas.create_text(
                self.margin + 10, self.margin + 10 + (10 * index),
                text=item,
                fill="white",
                font=("Determination Mono", 12, "normal"),
                anchor="w"
            )
            self.active_ui_elements.append(text)

        for index, item in enumerate(stats):
            text = self.game.canvas.create_text(
                self.margin + 30, self.margin + 10 + (10 * index),
                text=item,
                fill="white",
                font=("Determination Mono", 12, "normal"),
                anchor="w"
            )
            self.active_ui_elements.append(text)

        # Draw the buttons
        for index, item in enumerate(["ITEM", "STATS", "CELL"]):
            button = self.game.canvas.create_text(
                self.actionx1 + 30, self.action_y1 + 20 + (20 * index),
                text=item,
                fill="white",
                font=("Determination Mono", 24, "normal"),
                anchor="w"
            )
            self.active_ui_elements.append(button)

        # Draw the soul
        self.menu_soul = self.game.canvas.create_image(0, 0, image=self.game.player_sprite)


    def _draw_stats(self):
        """Draws player stats on the screen."""
        pass


    def _draw_item_list(self):
        """Loops thorough player's inventory and draws the items on the screen."""
        pass


    def _draw_action_box(self):
        """Draws the USE/INFO/THROW buttons on the screen."""
        pass


    def clear(self):
        """Closes everything and cleans up."""
        for element in self.active_ui_elements:
            self.game.canvas.delete(element)

        self.active_ui_elements.clear()
        self.is_active = False
        self.menu_index = 0
        self.layer_index = 0