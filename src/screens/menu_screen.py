from tkinter import messagebox
from pygame import mixer
from src.core.enums import Action

class MenuScreen:
    """The menu gets triggered if the player presses the [C] key."""

    def __init__(self, main_game):
        self.game = main_game
        self.margin = 32

        self.is_active = False
        self.menu_index = 0
        self.layer_index = 0

        self.active_ui_elements = []
        self.button_ids = []


    def open_menu(self, index=0):
        """Opens the menu with given index."""
        self.is_active = True

        self._draw_main_boxes(index=0)
        self._draw_menu_text()
        self.update_visuals()


    def close_menu(self, index=0):
        """Closes the menu with given index. If index is 0, everything is closed."""
        if index == 0: self.clear()


    def handle_input(self, input_mgr):
        """Handles keyboard inputs while a menu is open."""
        if input_mgr.is_just_pressed(Action.MENU):
            self.close_menu(index=0)
            return
        
        if input_mgr.is_just_pressed(Action.CANCEL):
            self.close_menu(self.layer_index)
            return

        if self.layer_index == 0: # Player is on the ITEM/STAT/CELL selection
            moved = False

            if input_mgr.is_just_pressed(Action.DOWN):
                if self.menu_index != 2:
                    self.menu_index += 1
                    moved = True

            if input_mgr.is_just_pressed(Action.UP):
                if self.menu_index != 0:
                    self.menu_index -= 1
                    moved = True

            if moved:
                mixer.Sound(file="sounds/sound_effects/snd_squeak.wav").play()
                self.update_visuals()


    def update_visuals(self):
        """Updates selection regarding to keypresses."""
        if self.layer_index == 0: # Player is on the ITEM/STAT/CELL selection
            x1, y1, x2, y2 = self.game.canvas.bbox(self.button_ids[self.menu_index])
            target_x = x1 - 20
            target_y = y1 + ((y2 - y1) // 2) + 3
            self.game.canvas.coords(self.menu_soul, target_x, target_y)


    def _draw_main_boxes(self, index):
        """Calculates and draws the core 3-box layout of the menu."""
        # Stats Box
        self.stats_x1 = self.margin
        self.stats_y1 = self.margin
        self.stats_x2 = self.margin + 140
        self.stats_y2 = self.margin + 110
        
        stats_box = self.game.canvas.create_rectangle(
            self.stats_x1, self.stats_y1, self.stats_x2, self.stats_y2,
            fill="black", outline="white", width=6
        )
        self.active_ui_elements.append(stats_box)

        # Action Box
        self.action_x1 = self.margin
        self.action_y1 = self.stats_y2 + 15
        self.action_x2 = self.stats_x2
        self.action_y2 = self.action_y1 + 155
        
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
            self.margin + 10, self.margin + 20,
            text=data["name"],
            fill="white",
            font=("Determination Mono", 26, "normal"),
            anchor="w"
        )
        self.active_ui_elements.append(name_text)

        for index, item in enumerate(["LV", "HP", "G"]):
            text = self.game.canvas.create_text(
                self.margin + 10, self.margin + 30 + (20 * (index + 1)),
                text=item,
                fill="white",
                font=("Determination Mono", 18, "normal"),
                anchor="w"
            )
            self.active_ui_elements.append(text)

        for index, item in enumerate(stats):
            text = self.game.canvas.create_text(
                self.margin + 50, self.margin + 30 + (20 * (index + 1)),
                text=item,
                fill="white",
                font=("Determination Mono", 18, "normal"),
                anchor="w"
            )
            self.active_ui_elements.append(text)

        # Draw the buttons
        for index, item in enumerate(["ITEM", "STAT", "CELL"]):
            button = self.game.canvas.create_text(
                self.action_x1 + 50, self.action_y1 + 35 + (40 * index),
                text=item,
                fill="white",
                font=("Determination Mono", 26, "normal"),
                anchor="w"
            )
            self.button_ids.append(button)
            self.active_ui_elements.append(button)

        # Draw the soul
        self.menu_soul = self.game.canvas.create_image(0, 0, image=self.game.player_sprite)
        self.active_ui_elements.append(self.menu_soul)


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
        self.button_ids.clear()
        self.is_active = False
        self.menu_soul = None
        self.menu_index = 0
        self.layer_index = 0