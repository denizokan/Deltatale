import sys
import pygame
from pygame import mixer
from src.core.enums import Action, Event
from src.core.constants import Constants, Color
from src.core.events import EventBus
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

    def __init__(self, asset_manager, save_system):
        """Initializes the file selection screen."""
        self.asset_manager = asset_manager
        self.save_system = save_system

        self.menu_index = 0
        self.selected_slot_index = None
        self.prompt_index = 0
        self.menu_soul_x, self.menu_soul_y = 0, 0

        self.save_slots = []
        for i in range(0, 3):
            try:
                self.save_slots.append(self.save_system.load_file(i))
            except RuntimeError as e:
                print(f"An error has occured: {e}")
                pygame.quit()
                sys.exit()

        self.title_text_str = "Please select a file."
        self.current_mode = ActionMode.SELECT

        self.menu_theme = self.asset_manager.get_sfx("menu_theme")
        self.squeak_sound = self.asset_manager.get_sfx("snd_squeak")
        self.select_sound = self.asset_manager.get_sfx("snd_select")
        self.swing_sound = self.asset_manager.get_sfx("snd_swing")
        self.menu_theme.play(loops=-1)


    def draw(self, screen):
        """Gets called every game tick to draw current visuals on the screen."""
        # Title Text
        font = self.asset_manager.get_font("dtm_sans_24")
        title_surf = font.render(self.title_text_str, False, Color.WHITE)
        title_rect = title_surf.get_rect(midleft=(90, 65))
        screen.blit(title_surf, title_rect)

        # Boxes
        box_width = Constants.WIDTH // 1.65
        box_height = 85
        start_y = 100
        spacing = 95
                
        for index, slot in enumerate(self.save_slots):
            x = (Constants.WIDTH - box_width) // 2
            y = start_y + (index * spacing)

            color = Color.GRAY
            if self.menu_index == index:
                color = Color.WHITE
            if self.selected_slot_index == index and (self.current_mode == ActionMode.COPY_TO or self.current_mode == ActionMode.ERASE):
                color = Color.RED
        
            rect = pygame.Rect(x, y, box_width, box_height)
            pygame.draw.rect(screen, color, rect, width=2)

            if self.selected_slot_index == index: # In a prompt
                prompt_msg = ""
                if self.current_mode == ActionMode.COPY_TO:
                    prompt_msg = f"Overwrite file slot {self.selected_slot_index + 1}?"
                elif self.current_mode == ActionMode.ERASE:
                    prompt_msg = f"Permanently erase file slot {self.selected_slot_index + 1}?"
                else:
                    if self.save_system.exists(self.selected_slot_index):
                        prompt_msg = f"Continue DELTATALE on slot {self.selected_slot_index + 1}?"
                    else:
                        prompt_msg = f"Start DELTATALE from slot {self.selected_slot_index + 1}?"

                # Prompt
                prompt_surf = font.render(prompt_msg, True, Color.WHITE)
                prompt_rect = prompt_surf.get_rect(center=(Constants.WIDTH // 2, y + 25))
                screen.blit(prompt_surf, prompt_rect)

                # Yes & No Buttons
                yes_surf = font.render("Yes", True, Color.WHITE if self.prompt_index == 0 else Color.GRAY)
                yes_rect = yes_surf.get_rect(midleft=(x + 80, y + 60))
                screen.blit(yes_surf, yes_rect)

                no_surf = font.render("No", True, Color.WHITE if self.prompt_index == 1 else Color.GRAY)
                no_rect = no_surf.get_rect(midright=(x + box_width - 80, y + 60))
                screen.blit(no_surf, no_rect)

            else:
                # Name
                name_surf = font.render(slot['name'], True, color)
                name_rect = name_surf.get_rect(midleft=(x + 60, y + 25))
                screen.blit(name_surf, name_rect)

                # Location
                location_surf = font.render(slot['location'], True, color)
                location_rect = location_surf.get_rect(midleft=(x + 60, y + 60))
                screen.blit(location_surf, location_rect)

                # Playtime
                playtime_surf = font.render(self._playtime_to_str(slot['playtime']), True, color)
                playtime_rect = playtime_surf.get_rect(midright=(x + box_width - 60, y + 25))
                screen.blit(playtime_surf, playtime_rect)

        # Copy, Erase, Quit Buttons
        start_x = (Constants.WIDTH - box_width) // 2
        btn_y = 410
    
        self.button_positions = [
            (start_x + 25, btn_y, "Copy"),
            (Constants.WIDTH // 2, btn_y, "Erase"),
            (start_x + box_width - 25, btn_y, "Quit")
        ]
    
        for index, button in enumerate(self.button_positions):
            color = Color.GRAY
            if self.menu_index == index + 3:
                color = Color.WHITE

            button_text = button[2]
            if button_text == "Copy" and (self.current_mode == ActionMode.COPY_FROM or self.current_mode == ActionMode.COPY_TO):
                button_text = "Cancel"

            if button_text == "Erase" and self.current_mode == ActionMode.ERASE:
                button_text = "Cancel"

            button_surf = font.render(button_text, True, color)
            button_rect = button_surf.get_rect(center=(button[0], button[1]))
            screen.blit(button_surf, button_rect)
    
        # Footer text & Kris/Susie
        footer_font = self.asset_manager.get_font("dtm_sans_16")
        footer_surf = footer_font.render("DELTATALE 0.0.1", True, Color.GRAY)
        footer_rect = footer_surf.get_rect(midright=(Constants.WIDTH - 5, Constants.HEIGHT - 15))
        screen.blit(footer_surf, footer_rect)

        kris_sprite = self.asset_manager.get_image("kris")["down"][0]
        susie_sprite = self.asset_manager.get_image("susie")["down"][0]

        kris_rect = kris_sprite.get_rect(center=(Constants.WIDTH // 2 - 30, Constants.HEIGHT - 8))
        susie_rect = susie_sprite.get_rect(center=(Constants.WIDTH // 2 + 30, Constants.HEIGHT - 8))
        
        screen.blit(kris_sprite, kris_rect)
        screen.blit(susie_sprite, susie_rect)

        # Create the soul/selector sprite
        menu_soul_sprite = self.asset_manager.get_image("spr_soul")
        soul_rect = menu_soul_sprite.get_rect(center=(self.menu_soul_x, self.menu_soul_y))
        screen.blit(menu_soul_sprite, soul_rect)


    def update_visuals(self):
        """Calculates text strings and SOUL cursor coordinates based on current state."""
        box_width = Constants.WIDTH // 1.65
        start_x = (Constants.WIDTH - box_width) // 2
        
        if self.selected_slot_index is not None:
            # Soul is pointing at Yes / No in a prompt
            start_y = 101 + (self.selected_slot_index * 95)
            if self.prompt_index == 0: # Pointing at Yes
                self.menu_soul_x = start_x + 60
            else: # Pointing at No
                self.menu_soul_x = start_x + box_width - 125
            self.menu_soul_y = start_y + 60

        elif self.menu_index <= 2:
            # Soul is pointing at a Save Slot
            self.menu_soul_x = start_x + 30
            self.menu_soul_y = 100 + (self.menu_index * 95) + 42
            
        else: 
            button_info = self.button_positions[self.menu_index - 3]
            self.menu_soul_x = button_info[0] - 45

            if self.menu_index == 3 and (self.current_mode == ActionMode.COPY_FROM or self.current_mode == ActionMode.COPY_TO):
                self.menu_soul_x = button_info[0] - 55
            if self.menu_index == 4:
                if self.current_mode == ActionMode.ERASE:
                    self.menu_soul_x = button_info[0] - 55
                else:
                    self.menu_soul_x = button_info[0] - 50

            self.menu_soul_y = button_info[1] + 1


    def handle_input(self, input_mgr):
        """
        This function gets triggered every game tick if the player is currently
        in the file select screen. Listens for keyboard inputs.
        """
        if self.selected_slot_index is not None:
            self.handle_prompt_input(input_mgr)
        else:
            self.handle_grid_input(input_mgr)

            
    def handle_grid_input(self, input_mgr):
        """This function handles navigation through the main file select screen."""
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
            self.update_title_text()
            self.squeak_sound.play()
        
        # Check for Confirm, Cancel Key Presses
        if input_mgr.is_just_pressed(Action.CONFIRM):
            if 0 <= self.menu_index <= 2: # Selected a save file
                self.select_sound.play()
                if self.current_mode == ActionMode.COPY_FROM:
                    self.copying_file_index = self.menu_index
                    for i in range(3):
                        if i != self.copying_file_index:
                            self.menu_index = i
                            break
                    self.current_mode = ActionMode.COPY_TO
                    self.title_text_str = "Select a slot to copy TO."
                    return
                
                if self.current_mode == ActionMode.COPY_TO:
                    self.selected_slot_index = self.menu_index
                    if self.save_system.exists(self.selected_slot_index):
                        # Override slot?
                        self.show_confirmation_prompt(self.menu_index)
                        return

                    try:
                        data = self.save_system.load_file(self.copying_file_index)
                        self.save_system.save_file(self.selected_slot_index, data)
                    except RuntimeError as e:
                        print(f"An error has occured: {e}")
                        pygame.quit()
                        sys.exit()

                    self.save_slots[self.selected_slot_index] = dict(self.save_slots[self.copying_file_index])

                    self.copying_file_index = None
                    self.selected_slot_index = None
                    self.current_mode = ActionMode.SELECT
                    self.update_visuals()
                    self.title_text_str = "File copied."
                    return
                
                if self.current_mode == ActionMode.ERASE:
                    self.selected_slot_index = self.menu_index
                    self.show_confirmation_prompt(self.menu_index)
                    return

                self.show_confirmation_prompt(self.menu_index)
            elif self.menu_index == 3: # Selected Copy/Cancel
                if self.current_mode == ActionMode.COPY_FROM or self.current_mode == ActionMode.COPY_TO:
                    self.swing_sound.play()
                    self.current_mode = ActionMode.SELECT
                    self.title_text_str = "Please select a file."
                    self.menu_index = 0
                    self.copying_file_index = None
                    self.selected_slot_index = None
                    self.update_visuals()
                    return

                eligable_index = None
                for index in range(3):
                    if self.save_system.exists(index):
                        eligable_index = index
                        break

                if eligable_index == None:
                    self.swing_sound.play()
                    self.title_text_str = "No files to copy."
                    return

                self.select_sound.play()
                self.current_mode = ActionMode.COPY_FROM
                self.title_text_str = "Select a file to copy."
                self.menu_index = eligable_index
                self.update_visuals()

            elif self.menu_index == 4: # Selected Erase/Cancel
                if self.current_mode == ActionMode.ERASE:
                    self.swing_sound.play()
                    self.current_mode = ActionMode.SELECT
                    self.title_text_str = "Please select a file."
                    self.menu_index = 0
                    self.update_visuals()
                    return
                
                eligable_index = None
                for index in range(3):
                    if self.save_system.exists(index):
                        eligable_index = index
                        break

                if eligable_index == None:
                    self.swing_sound.play()
                    self.title_text_str = "No files to erase."
                    return
                
                self.select_sound.play()
                self.current_mode = ActionMode.ERASE
                self.title_text_str = "Select a file to erase."
                self.menu_index = eligable_index
                self.update_visuals()

            elif self.menu_index == 5: # Selected Quit
                pygame.quit()
                sys.exit()

        if input_mgr.is_just_pressed(Action.CANCEL):
            if self.current_mode == ActionMode.COPY_FROM or self.current_mode == ActionMode.COPY_TO or self.current_mode == ActionMode.ERASE:
                self.swing_sound.play()
                self.current_mode = ActionMode.SELECT
                self.title_text_str = "Please select a file."
                self.copying_file_index = None
                self.selected_slot_index = None
                self.update_visuals()
                return
            

    def handle_prompt_input(self, input_mgr):
        """This function handles navigation through confirmation menus."""
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
            self.squeak_sound.play()
            self.update_visuals()

        if input_mgr.is_just_pressed(Action.CONFIRM):
            if self.prompt_index == 0: # Start the game / Do the action
                self.select_sound.play()
                if self.current_mode == ActionMode.COPY_TO: # Overwriting a slot
                    try:
                        data = self.save_system.load_file(self.copying_file_index)
                        self.save_system.save_file(self.selected_slot_index, data)
                    except RuntimeError as e:
                        print(f"An error has occured: {e}")
                        pygame.quit()
                        sys.exit()

                    self.save_slots[self.selected_slot_index] = dict(self.save_slots[self.copying_file_index])

                    self.close_prompt()
                    self.update_visuals()
                    self.title_text_str = "File copied."
                    return
                
                if self.current_mode == ActionMode.ERASE:
                    try:
                        self.save_system.delete_file(self.selected_slot_index)
                    except RuntimeError as e:
                        print(f"An error has occured: {e}")
                        pygame.quit()
                        sys.exit()

                    self.save_slots[self.selected_slot_index] = {"name": "[EMPTY]", "location": "--------", "playtime": "0", "isEmpty": True}

                    self.close_prompt()
                    self.update_visuals()
                    self.title_text_str = "File erased."
                    return

                # --- Start the game! ---
                self.start_game_transition()
            else:
                self.select_sound.play()
                self.title_text_str = "Please select a file."
                self.close_prompt()
            self.update_visuals()

        if input_mgr.is_just_pressed(Action.CANCEL):
            self.swing_sound.play()
            self.title_text_str = "Please select a file."
            self.close_prompt()
            self.update_visuals()
        return


    def update_title_text(self):
        """Only gets triggered when the soul moves through the menu."""
        if self.current_mode == ActionMode.COPY_FROM:
            self.title_text_str = "Select a file to copy."
        elif self.current_mode == ActionMode.COPY_TO:
            self.title_text_str = "Select a slot to copy TO."
        elif self.current_mode == ActionMode.ERASE:
            self.title_text_str = "Select a file to erase."
        elif self.current_mode == ActionMode.SELECT:
            self.title_text_str = "Please select a file."
    

    def get_next_valid_slot(self, start_idx, stop_idx, step):
        """Helper to find the next valid slot based on the current mode."""
        for i in range(start_idx, stop_idx, step):
            if self.current_mode in (ActionMode.COPY_FROM, ActionMode.ERASE):
                if self.save_system.exists(i):
                    return i
            elif self.current_mode == ActionMode.COPY_TO:
                if self.copying_file_index != i:
                    return i
        return None


    def show_confirmation_prompt(self, slot_index):
        """Prepares the UI to show the Yes/No confirmation prompt."""
        self.selected_slot_index = slot_index
        self.prompt_index = 0


    def close_prompt(self):
        self.prompt_index = 0
        self.selected_slot_index = None
        self.copying_file_index = None
        self.current_mode = ActionMode.SELECT


    def start_game_transition(self):
        """Initiates the game loading sequence."""
        self.menu_theme.fadeout(1500)
        EventBus.emit(Event.START_GAME, self.selected_slot_index)


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