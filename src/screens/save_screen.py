import sys
import pygame
from pygame import mixer
from src.core.enums import Action
from src.core.constants import Constants, Color

class SaveScreen:
    """This class gets called when a player interacts with a save point."""

    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        
        self.is_active = False
        self.menu_index = 0
        self.saved = False
        self.menu_soul_x, self.menu_soul_y = (Constants.WIDTH // 2) - ((Constants.WIDTH // 1.65) // 3) - 20, 250
        self.data = None
        self.interactable = None

        self.squeak_sound = self.asset_manager.get_sfx("snd_squeak")
        self.save_sound = self.asset_manager.get_sfx("snd_save")


    def show_save_screen(self, current_data, interactable, on_save_callback):
        """Stops movement inputs and shows the save screen."""
        self.data = current_data
        self.interactable = interactable
        self.on_save_callback = on_save_callback

        self.menu_index = 0
        self.saved = False
        self.is_active = True


    def draw(self, screen):
        """Draws to the screen every game tick while a save screen is active."""
        if not self.is_active: return

        self.box_width = Constants.WIDTH // 1.65
        self.box_height = 170
        self.start_y = 120
        
        self.box_x = (Constants.WIDTH - self.box_width) // 2
        self.box_y = self.start_y

        pygame.draw.rect(screen, Color.BLACK, (self.box_x, self.box_y, self.box_width, self.box_height))
        border_rect = pygame.Rect((self.box_x, self.box_y, self.box_width, self.box_height)).inflate(6, 6)
        pygame.draw.rect(screen, Color.WHITE, border_rect, 6)

        font = self.asset_manager.get_font("dtm_sans_26")
        color = Color.WHITE
        save_text = "Save"
        if self.saved:
            color = Color.YELLOW
            save_text = "File saved."

        # Name Text
        name_surf = font.render(self.data["name"], False, color)
        name_rect = name_surf.get_rect(midleft=(self.box_x + 30, self.box_y + 35))
        screen.blit(name_surf, name_rect)

        # Level Text
        level_surf = font.render(f"LV {self.data["level"]}", False, color)
        level_rect = level_surf.get_rect(center=(Constants.WIDTH // 2, self.box_y + 35))
        screen.blit(level_surf, level_rect)

        # Playtime Text
        playtime_surf = font.render(self._playtime_to_str(self.data["playtime"]), False, color)
        playtime_rect = playtime_surf.get_rect(midright=(self.box_x + self.box_width - 30, self.box_y + 35))
        screen.blit(playtime_surf, playtime_rect)

        # Location Text
        location_surf = font.render(self.data["location"], False, color)
        location_rect = location_surf.get_rect(midleft=(self.box_x + 30, self.box_y + 75))
        screen.blit(location_surf, location_rect)
        
        # Create the buttons
        save_surf = font.render(save_text, False, color)
        save_rect = save_surf.get_rect(midleft=((Constants.WIDTH // 2) - ((Constants.WIDTH // 1.65) // 3), self.box_y + 130))
        screen.blit(save_surf, save_rect)

        if not self.saved:
            return_surf = font.render("Return", False, color)
            return_rect = return_surf.get_rect(midright=((Constants.WIDTH // 2) + ((Constants.WIDTH // 1.65) // 3), self.box_y + 130))
            screen.blit(return_surf, return_rect)
        
            # Draw the SOUL sprite
            menu_soul_sprite = self.asset_manager.get_image("spr_soul")
            soul_rect = menu_soul_sprite.get_rect(center=(self.menu_soul_x, self.menu_soul_y))
            screen.blit(menu_soul_sprite, soul_rect)
        

    def handle_input(self, input_mgr):
        if not self.is_active: return

        if input_mgr.is_just_pressed(Action.CONFIRM):
            if self.saved:
                self.clear()
                return
            
            if self.menu_index == 0: # Player pressed save
                self.data = self.on_save_callback(self.interactable)
                self.saved = True
                self.save_sound.play()
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
            self.squeak_sound.play()


    def update(self):
        """
        Calculates the exact screen coordinates for the SOUL cursor based on the 
        current menu_index state.
        """
        if not self.is_active: return

        if not self.saved: # Navigating the buttons
            self.menu_soul_x = (Constants.WIDTH // 2) - ((Constants.WIDTH // 1.65) // 3) - 20
            if self.menu_index == 1:
                self.menu_soul_x = (Constants.WIDTH // 2) + ((Constants.WIDTH // 1.65) // 3) - 105
            self.menu_soul_y = self.box_y + 130


    def clear(self):
        """Cleans up variables."""
        self.box_x = None
        self.box_y = None
        self.box_width = None
        self.box_height = None
        self.menu_index = 0
        self.menu_soul_x, self.menu_soul_y = (Constants.WIDTH // 2) - ((Constants.WIDTH // 1.65) // 3) - 20, 250
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