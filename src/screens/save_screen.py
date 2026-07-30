from tkinter import messagebox
from pygame import mixer
from src.core.enums import Action

class SaveScreen:
    """This class gets called when a player interacts with a save point."""

    def __init__(self, main_game):
        self.game = main_game

        self.is_active = False
        self.menu_index = 0
        self.saved = False

        self.active_ui_elements = []
        self.ids = {
            "box": None,
            "name": None,
            "level": None,
            "playtime": None,
            "location": None
        }
        self.button_ids = []


    def show_save_screen(self, interactable):
        """Stops movement inputs and shows the save screen."""
        save_index = self.game.selected_file_index

        try:
            old_data = self.game.save_system.load_file(save_index)
        except RuntimeError as e:
            self.game.root.destroy()
            messagebox.showerror(
                "An error has occured.",
                f"{e}"
            )
            exit(1)

        self.is_active = True
        self.old_data = old_data
        self.interactable = interactable

        self.draw_box()
        self.draw_text(old_data)
        self.update_visuals()
        

    def handle_input(self, input_mgr):
        """Handles keyboard input while a save screen is active."""
        if not self.is_active: return

        # Listen for confirm/cancel inputs
        if input_mgr.is_just_pressed(Action.CONFIRM):
            if self.saved:
                self.clear()
                return
            
            if self.menu_index == 0: # Player pressed save
                new_save = self.overwrite_data(self.old_data, self.interactable)
                self.save(new_save)
                return

            if self.menu_index == 1: # Player pressed cancel
                self.clear()
                return
        
        if input_mgr.is_just_pressed(Action.CANCEL):
            self.clear()
            return

        if self.saved: return

        moved = False
        if input_mgr.is_just_pressed(Action.LEFT):
            if self.menu_index != 0:
                self.menu_index -= 1
                moved = True

        if input_mgr.is_just_pressed(Action.RIGHT):
            if self.menu_index == 0:
                self.menu_index += 1
                moved = True

        if moved:
            mixer.Sound(file="sounds/sound_effects/snd_squeak.wav").play()
            self.update_visuals()


    def save(self, new_data):
        """Saves the game and updates text on the screen."""
        if self.saved: return

        self.saved = True
        try:
            self.game.save_system.save_file(self.game.selected_file_index, new_data)
        except RuntimeError as e:
            self.game.root.destroy()
            messagebox.showerror(
                "An error has occured.",
                f"{e}"
            )
            exit(1)

        save_sound = mixer.Sound(file="sounds/sound_effects/snd_save.wav")
        save_sound.play()
        self.update_visuals(new_data)


    def update_visuals(self, new_data=None):
        """
        Calculates the exact screen coordinates for the SOUL cursor based on the 
        current menu_index state, then moves the canvas image component to match.
        """
        if not self.saved: # Navigating the buttons
            x1, y1, x2, y2 = self.game.canvas.bbox(self.button_ids[self.menu_index])
            target_x = x1 - 20
            target_y = self.box_y1 + 130
            self.game.canvas.coords(self.menu_soul, target_x, target_y)
        else: # Saved the game
            self.game.canvas.itemconfig(self.ids["name"], fill="yellow")
            self.game.canvas.itemconfig(self.ids["level"], text=f"LV {new_data["level"]}", fill="yellow")
            self.game.canvas.itemconfig(self.ids["playtime"], text=self._playtime_to_str(new_data["playtime"]), fill="yellow")
            self.game.canvas.itemconfig(self.ids["location"], text=new_data["location"], fill="yellow")
            self.game.canvas.delete(self.menu_soul)
            self.game.canvas.delete(self.button_ids[1])
            self.game.canvas.itemconfig(self.button_ids[0], text="File saved.", fill="yellow")
            

    def overwrite_data(self, old_data, interactable):
        """Overwrites old save data with the new data."""
        old_data["location"] = interactable["location"]
        old_data["playtime"] += self.game.playtime
        old_data["room"] = self.game.current_room.room_id
        old_data["flags"] = self.game.flags
        self.game.playtime = 0
        # TODO: Update more values later

        new_data = old_data
        return new_data


    def draw_box(self):
        """Draws the save box on the screen."""
        box_width = self.game.constants.WIDTH // 1.65
        box_height = 170
        start_y = 120

        self.box_x1 = (self.game.constants.WIDTH - box_width) // 2
        self.box_x2 = self.box_x1 + box_width
        self.box_y1 = start_y
        self.box_y2 = self.box_y1 + box_height

        save_box = self.game.canvas.create_rectangle(
            self.box_x1,
            self.box_y1,
            self.box_x2,
            self.box_y2,
            fill="black",
            outline="white",
            width=6
        )
        self.active_ui_elements.append(save_box)
        self.ids["box"] = save_box


    def draw_text(self, old_data):
        """Draws info text on top of the save box."""
        name_text = self.game.canvas.create_text(
            self.box_x1 + 30,
            self.box_y1 + 35,
            text=old_data["name"],
            fill="white",
            font=("Determination Sans", 26, "normal"),
            anchor="w"
        )

        level_text = self.game.canvas.create_text(
            self.game.constants.WIDTH // 2,
            self.box_y1 + 35,
            text=f"LV {old_data["level"]}",
            fill="white",
            font=("Determination Sans", 26, "normal"),
            anchor="center"
        )

        playtime_text = self.game.canvas.create_text(
            self.box_x2 - 30,
            self.box_y1 + 35,
            text=self._playtime_to_str(old_data["playtime"]),
            fill="white",
            font=("Determination Sans", 26, "normal"),
            anchor="e"
        )

        location_text = self.game.canvas.create_text(
            self.box_x1 + 30,
            self.box_y1 + 75,
            text=old_data["location"],
            fill="white",
            font=("Determination Sans", 26, "normal"),
            anchor="w"
        )

        # Create the buttons
        save_button = self.game.canvas.create_text(
            (self.game.constants.WIDTH // 2) - ((self.game.constants.WIDTH // 1.65) // 3),
            self.box_y1 + 130,
            text="Save",
            fill="white",
            font=("Determination Sans", 26, "normal"),
            anchor="w"
        )

        return_button = self.game.canvas.create_text(
            (self.game.constants.WIDTH // 2) + ((self.game.constants.WIDTH // 1.65) // 3),
            self.box_y1 + 130,
            text="Return",
            fill="white",
            font=("Determination Sans", 26, "normal"),
            anchor="e"
        )

        # Draw the SOUL sprite
        self.menu_soul = self.game.canvas.create_image(0, 0, image=self.game.player_sprite)

        self.ids["name"] = name_text
        self.ids["level"] = level_text
        self.ids["playtime"] = playtime_text
        self.ids["location"] = location_text

        self.button_ids.extend([save_button, return_button])
        self.active_ui_elements.extend([name_text, level_text, playtime_text, location_text, save_button, return_button, self.menu_soul])


    def clear(self):
        """Cleans up and clears the save box / text from the screen."""
        for element in self.active_ui_elements:
            self.game.canvas.delete(element)

        self.active_ui_elements.clear()
        self.button_ids.clear()
        self.ids.clear()
        self.box_x1 = None
        self.box_x2 = None
        self.box_y1 = None
        self.box_y2 = None
        self.menu_index = 0
        self.is_active = False
        self.interactable = None
        self.old_data = None
        self.new_save = None
        self.saved = False
        self.menu_soul = None


    def _playtime_to_str(self, num):
        """This function takes an integer and converts it into MM:SS format."""
        playtime = int(num)
        minutes = 0
        seconds = 0

        while playtime > 0:
            if playtime >= 60:
                playtime -= 60
                minutes += 1
            else:
                seconds = playtime
                playtime = 0

        minutes_str = minutes
        if minutes == 0 and seconds == 0:
            minutes_str = "--"
        if minutes < 10:
            minutes_str = f"0{minutes}"

        seconds_str = seconds
        if seconds == 0 and minutes == 0:
            seconds_str = "--"
        if seconds < 10:
            seconds_str = f"0{seconds}"

        return f"{minutes_str}:{seconds_str}"