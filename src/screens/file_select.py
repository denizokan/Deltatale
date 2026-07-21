from pygame import mixer
from src.core.enums import Action
from tkinter import PhotoImage, messagebox
from enum import Enum, auto

class ActionMode(Enum):
    SELECT = auto()
    COPY_FROM = auto()
    COPY_TO = auto()
    ERASE = auto()

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
        self.selected_slot_index = None
        self.prompt_index = 0
        self.title_text_id = None
        self.active_ui_elements = []
        self.prompt_ui_elements = []
        self.ui_positions = []
        self.slot_visual_ids = []
        
        self.current_mode = ActionMode.SELECT
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
        self.title_text_id = title_text
        self.active_ui_elements.append(title_text)

        # --- Box Variables ---
        box_width = self.game.constants.WIDTH // 1.65
        box_height = 85
        start_y = 100
        spacing = 95

        save_slots = []
        for i in range(0, 3):
            try:
                save_slots.append(self.game.save_system.load_file(i))
            except RuntimeError as e:
                self.game.root.destroy()
                messagebox.showerror(
                    "An error has occured.",
                    f"{e}"
                )
                exit(1)

        # Create the save slot boxes & their texts
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
            playtime_text = self.game.canvas.create_text(
                x2 - 60,
                y1 + 25,
                text=self.playtime_to_str(slot['playtime']),
                fill="gray",
                font=("Determination Sans", 24, "normal"),
                anchor="e"
            )

            self.active_ui_elements.extend([name_text, location_text, playtime_text])
            self.slot_visual_ids.append({
                "box": save_slot_box,
                "name": name_text,
                "location": location_text,
                "playtime": playtime_text
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

        # Footer text & Kris/Susie
        footer_text = self.game.canvas.create_text(
            self.game.constants.WIDTH - 5,
            self.game.constants.HEIGHT - 15,
            text="DELTATALE 0.0.1",
            fill="gray",
            font=("Determination Sans", 16, "normal"),
            anchor="e"
        )
        self.kris_sprite_image = PhotoImage(file="sprites/DELTARUNE Sprites/Characters/Playable Characters/Kris/Ch1/Light World/spr_krisd_0.png").zoom(2)
        kris_sprite = self.game.canvas.create_image(self.game.constants.WIDTH // 2 - 30, self.game.constants.HEIGHT - 8, image=self.kris_sprite_image)

        self.susie_sprite_image = PhotoImage(file="sprites/DELTARUNE Sprites/Characters/Playable Characters/Susie/Ch1/Light World/Walk/spr_susied_0.png").zoom(2)
        susie_sprite = self.game.canvas.create_image(self.game.constants.WIDTH // 2 + 30, self.game.constants.HEIGHT - 8, image=self.susie_sprite_image)

        self.active_ui_elements.extend([footer_text, kris_sprite, susie_sprite])

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

        # --- If modes are active ---
        if self.current_mode == ActionMode.COPY_FROM:
            self.game.canvas.itemconfig(self.title_text_id, text="Select a file to copy.")
            self.game.canvas.itemconfig(self.button_visual_ids[0], text="Cancel")
            self.game.canvas.itemconfig(self.button_visual_ids[1], text="Erase")

        if self.current_mode == ActionMode.COPY_TO:
            self.game.canvas.itemconfig(self.title_text_id, text="Select a slot to copy TO.")
            self.game.canvas.itemconfig(self.button_visual_ids[0], text="Cancel")
            self.game.canvas.itemconfig(self.button_visual_ids[1], text="Erase")

        if self.current_mode == ActionMode.ERASE:
            self.game.canvas.itemconfig(self.title_text_id, text="Select a file to erase.")
            self.game.canvas.itemconfig(self.button_visual_ids[0], text="Copy")
            self.game.canvas.itemconfig(self.button_visual_ids[1], text="Cancel")

        if self.current_mode == ActionMode.SELECT:
            self.game.canvas.itemconfig(self.title_text_id, text="Please select a file.", fill="white")
            self.game.canvas.itemconfig(self.button_visual_ids[0], text="Copy")
            self.game.canvas.itemconfig(self.button_visual_ids[1], text="Erase")

        # --- If player is in a confirmation screen ---
        if self.selected_slot_index is not None:
            button_id = self.prompt_ui_elements[self.prompt_index + 1]
            coords = self.ui_positions[self.selected_slot_index]
            target_x = self.game.canvas.bbox(button_id)[0] - 20
            target_y = coords[1] + 60

            self.game.canvas.coords(self.menu_soul, target_x, target_y)

            button_elements = self.prompt_ui_elements[1:]
            for index, button in enumerate(button_elements):
                if self.prompt_index == index:
                    self.game.canvas.itemconfig(button, fill="white")
                else:
                    self.game.canvas.itemconfig(button, fill="gray")

            return
        # ------------------

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
                self.game.canvas.itemconfig(slot['playtime'], fill="white")
            else:
                self.game.canvas.itemconfig(slot['box'], outline="gray")
                self.game.canvas.itemconfig(slot['name'], fill="gray")
                self.game.canvas.itemconfig(slot['location'], fill="gray")
                self.game.canvas.itemconfig(slot['playtime'], fill="gray")
        for index, button in enumerate(self.button_visual_ids):
            if self.menu_index == index + 3:
                self.game.canvas.itemconfig(button, fill="white")
            else:
                self.game.canvas.itemconfig(button, fill="gray")


    def handle_input(self):
        """
        This function gets triggered every game tick if the player is currently
        in the file select screen. Listens for keyboard inputs.
        """
        if self.selected_slot_index is not None:
            self.handle_prompt_input()
        else:
            self.handle_grid_input()

            
    def handle_grid_input(self):
        """This function handles navigation through the main file select screen."""
        input_mgr = self.game.input_manager
        moved = False

        if input_mgr.is_just_pressed(Action.UP):
            if self.menu_index >= 3: # On the buttons
                if self.current_mode != ActionMode.SELECT:
                    target = self.get_next_valid_slot(2, -1, -1)
                    if target is not None:
                        self.menu_index = target
                        moved = True
                else:
                    self.menu_index = 2
                    moved = True
            elif self.menu_index > 0: # On the slots
                if self.current_mode != ActionMode.SELECT:
                    target = self.get_next_valid_slot(self.menu_index - 1, -1, -1)
                    if target is not None:
                        self.menu_index = target
                        moved = True
                else:
                    self.menu_index -= 1
                    moved = True

        if input_mgr.is_just_pressed(Action.DOWN):
            if self.menu_index < 3: # On the slots
                if self.current_mode != ActionMode.SELECT:
                    target = self.get_next_valid_slot(self.menu_index + 1, 3, 1)
                    if target is not None:
                        self.menu_index = target
                    else:
                        self.menu_index = 3
                    moved = True
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
            mixer.Sound(file="sounds/undertale_sounds/snd_squeak.wav").play()
            self.update_visuals()
        
        # Check for Confirm, Cancel Key Presses
        if input_mgr.is_just_pressed(Action.CONFIRM):
            if 0 <= self.menu_index <= 2: # Selected a save file
                mixer.Sound("sounds/undertale_sounds/snd_select.wav").play()
                if self.current_mode == ActionMode.COPY_FROM:
                    self.copying_file_index = self.menu_index
                    for i in range(3):
                        if i != self.copying_file_index:
                            self.menu_index = i
                            break
                    self.current_mode = ActionMode.COPY_TO
                    self.update_visuals()
                    return
                
                if self.current_mode == ActionMode.COPY_TO:
                    self.selected_slot_index = self.menu_index
                    if self.game.save_system.exists(self.selected_slot_index):
                        # Override slot?
                        self.show_confirmation_prompt(self.menu_index)
                        return

                    try:
                        data = self.game.save_system.load_file(self.copying_file_index)
                        self.game.save_system.save_file(self.selected_slot_index, data)
                    except RuntimeError as e:
                        self.game.root.destroy()
                        messagebox.showerror(
                            "An error has occured.",
                            f"{e}"
                        )
                        exit(1)

                    for element in self.slot_visual_ids[self.selected_slot_index]:
                        if element == "box": continue
                        source_text = self.game.canvas.itemcget(self.slot_visual_ids[self.copying_file_index][element], "text")
                        self.game.canvas.itemconfig(self.slot_visual_ids[self.selected_slot_index][element], text=source_text)

                    self.copying_file_index = None
                    self.selected_slot_index = None
                    self.current_mode = ActionMode.SELECT
                    self.update_visuals()
                    self.game.canvas.itemconfig(self.title_text_id, text="File copied.")
                    return
                
                if self.current_mode == ActionMode.ERASE:
                    self.selected_slot_index = self.menu_index
                    self.show_confirmation_prompt(self.menu_index)
                    return

                self.show_confirmation_prompt(self.menu_index)
            elif self.menu_index == 3: # Selected Copy/Cancel
                if self.current_mode == ActionMode.COPY_FROM or self.current_mode == ActionMode.COPY_TO:
                    mixer.Sound("sounds/deltarune_sounds/snd_swing.wav").play()
                    self.current_mode = ActionMode.SELECT
                    self.menu_index = 0
                    self.copying_file_index = None
                    self.selected_slot_index = None
                    self.update_visuals()
                    return

                eligable_index = None
                for index in range(3):
                    if self.game.save_system.exists(index):
                        eligable_index = index
                        break

                if eligable_index == None:
                    mixer.Sound("sounds/deltarune_sounds/snd_swing.wav").play()
                    self.game.canvas.itemconfig(self.title_text_id, text="No files to copy.")
                    return

                mixer.Sound("sounds/undertale_sounds/snd_select.wav").play()
                self.current_mode = ActionMode.COPY_FROM
                self.menu_index = eligable_index
                self.update_visuals()

            elif self.menu_index == 4: # Selected Erase/Cancel
                if self.current_mode == ActionMode.ERASE:
                    mixer.Sound("sounds/deltarune_sounds/snd_swing.wav").play()
                    self.current_mode = ActionMode.SELECT
                    self.menu_index = 0
                    self.update_visuals()
                    return
                
                eligable_index = None
                for index in range(3):
                    if self.game.save_system.exists(index):
                        eligable_index = index
                        break

                if eligable_index == None:
                    mixer.Sound("sounds/deltarune_sounds/snd_swing.wav").play()
                    self.game.canvas.itemconfig(self.title_text_id, text="No files to erase.")
                    return
                
                mixer.Sound("sounds/undertale_sounds/snd_select.wav").play()
                self.current_mode = ActionMode.ERASE
                self.menu_index = eligable_index
                self.update_visuals()

            elif self.menu_index == 5: # Selected Quit
                self.game.root.destroy()
                exit()

        if input_mgr.is_just_pressed(Action.CANCEL):
            if self.current_mode == ActionMode.COPY_FROM or self.current_mode == ActionMode.COPY_TO or self.current_mode == ActionMode.ERASE:
                mixer.Sound("sounds/deltarune_sounds/snd_swing.wav").play()
                self.current_mode = ActionMode.SELECT
                self.copying_file_index = None
                self.selected_slot_index = None
                self.update_visuals()
                return
            

    def handle_prompt_input(self):
        """This function handles navigation through confirmation menus."""
        input_mgr = self.game.input_manager
        moved = False

        if input_mgr.is_just_pressed(Action.LEFT):
            if self.prompt_index == 1:
                self.prompt_index -= 1
                moved = True
        
        if input_mgr.is_just_pressed(Action.RIGHT):
            if self.prompt_index == 0:
                self.prompt_index += 1
                moved = True

        if moved:
            mixer.Sound(file="sounds/undertale_sounds/snd_squeak.wav").play()
            self.update_visuals()

        if input_mgr.is_just_pressed(Action.CONFIRM):
            if self.prompt_index == 0: # Start the game / Do the action
                mixer.Sound("sounds/undertale_sounds/snd_select.wav").play()
                if self.current_mode == ActionMode.COPY_TO: # Overwriting a slot
                    try:
                        data = self.game.save_system.load_file(self.copying_file_index)
                        self.game.save_system.save_file(self.selected_slot_index, data)
                    except RuntimeError as e:
                        self.game.root.destroy()
                        messagebox.showerror(
                            "An error has occured.",
                            f"{e}"
                        )
                        exit(1)

                    self.close_prompt()
                    self.update_visuals()
                    self.game.canvas.itemconfig(self.title_text_id, text="File copied.")
                    return
                
                if self.current_mode == ActionMode.ERASE:
                    try:
                        self.game.save_system.delete_file(self.selected_slot_index)
                    except RuntimeError as e:
                        self.game.root.destroy()
                        messagebox.showerror(
                            "An error has occured.",
                            f"{e}"
                        )
                        exit(1)

                    self.close_prompt()
                    self.update_visuals()
                    self.game.canvas.itemconfig(self.title_text_id, text="File erased.")
                    return


                # --- Start the game! ---
                pass
            else:
                mixer.Sound("sounds/undertale_sounds/snd_select.wav").play()
                self.close_prompt()
            self.update_visuals()

        if input_mgr.is_just_pressed(Action.CANCEL):
            mixer.Sound("sounds/deltarune_sounds/snd_swing.wav").play()
            self.close_prompt()
            self.update_visuals()
        return
    

    def get_next_valid_slot(self, start_idx, stop_idx, step):
        """Helper to find the next valid slot based on the current mode."""
        for i in range(start_idx, stop_idx, step):
            if self.current_mode in (ActionMode.COPY_FROM, ActionMode.ERASE):
                if self.game.save_system.exists(i):
                    return i
            elif self.current_mode == ActionMode.COPY_TO:
                if self.copying_file_index != i:
                    return i
        return None


    def show_confirmation_prompt(self, slot_index):
        """This function gets triggered whenever a save slot gets selected or is about to be changed."""

        prompt_msg = ""
        if self.current_mode == ActionMode.COPY_TO:
            prompt_msg = f"Overwrite file slot {slot_index + 1}?"
        elif self.current_mode == ActionMode.ERASE:
            prompt_msg = f"Permanently erase file slot {slot_index + 1}?"
        else:
            if self.game.save_system.exists(slot_index):
                prompt_msg = f"Continue DELTATALE on slot {slot_index + 1}?"
            else:
                prompt_msg = f"Start DELTATALE from slot {slot_index + 1}?"

        self.selected_slot_index = slot_index

        for element in self.slot_visual_ids[slot_index]:
            if element == "box": continue
            self.active_ui_elements.remove(self.slot_visual_ids[slot_index][element])
            self.game.canvas.delete(self.slot_visual_ids[slot_index][element])
        
        coords = self.ui_positions[slot_index]
        prompt_text = self.game.canvas.create_text(
            self.game.constants.WIDTH // 2,
            coords[1] + 25,
            text=prompt_msg,
            fill="white",
            font=("Determination Sans", 24, "normal"),
            anchor="center"
        )

        # Buttons
        yes_button = self.game.canvas.create_text(
            coords[0] + 80,
            coords[1] + 60,
            text="Yes",
            fill="white",
            font=("Determination Sans", 24, "normal"),
            anchor="w"
        )
        no_button = self.game.canvas.create_text(
            coords[2] - 80,
            coords[1] + 60,
            text="Go Back",
            fill="gray",
            font=("Determination Sans", 24, "normal"),
            anchor = "e"
        )
        self.prompt_ui_elements.extend([prompt_text, yes_button, no_button])
        self.active_ui_elements.extend([prompt_text, yes_button, no_button])
        self.update_visuals()


    def close_prompt(self):
        for element in self.prompt_ui_elements:
            self.active_ui_elements.remove(element)
            self.game.canvas.delete(element)
        self.prompt_index = 0
        self.prompt_ui_elements.clear()
        self.restore_slot_info(self.selected_slot_index)
        self.selected_slot_index = None
        self.copying_file_index = None
        self.current_mode = ActionMode.SELECT


    def restore_slot_info(self, slot_index):
        """Restores the save data information for a specific save slot after backing out from a confirmation menu."""
        coords = self.ui_positions[slot_index]
        save_slot = self.game.save_system.load_file(slot_index)

        name_text = self.game.canvas.create_text(
            coords[0] + 60,
            coords[1] + 25,
            text=f"{save_slot['name']}",
            fill="white",
            font=("Determination Sans", 24, "normal"),
            anchor="w"
        )
        location_text = self.game.canvas.create_text(
            coords[0] + 60,
            coords[1] + 60,
            text=f"{save_slot['location']}",
            fill="white",
            font=("Determination Sans", 24, "normal"),
            anchor="w"
        )
        playtime_text = self.game.canvas.create_text(
            coords[2] - 60,
            coords[1] + 25,
            text=self.playtime_to_str(save_slot['playtime']),
            fill="white",
            font=("Determination Sans", 24, "normal"),
            anchor="e"
        )

        self.active_ui_elements.extend([name_text, location_text, playtime_text])
        box_id = self.slot_visual_ids[slot_index]["box"]
        self.slot_visual_ids[slot_index] = {
            "box": box_id,
            "name": name_text,
            "location": location_text,
            "playtime": playtime_text
        }


    def playtime_to_str(self, num):
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
        if minutes < 10:
            minutes_str = f"0{minutes}"
        if minutes == 0:
            minutes_str = "--"

        seconds_str = seconds
        if seconds < 10:
            seconds_str = f"0{seconds}"
        if seconds == 0:
            seconds_str = "--"

        return f"{minutes_str}:{seconds_str}"