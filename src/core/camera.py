from src.core.constants import Constants

class Camera:
    """For tracking the player."""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.screen_width = Constants.WIDTH
        self.screen_height = Constants.HEIGHT

    
    def update(self, player, current_room):
        """Updates the camera x, y."""
        room_width = current_room.bg_image.get_width()
        room_height = current_room.bg_image.get_height()

        target_x = player.x - (self.screen_width / 2)
        target_y = player.y - (self.screen_height / 2)

        max_scroll_x = room_width - self.screen_width
        max_scroll_y = room_height - self.screen_height
        
        self.x = max(0, min(target_x, max_scroll_x))
        self.y = max(0, min(target_y, max_scroll_y))

        if room_width < self.screen_width:
            self.x = -(self.screen_width - room_width) / 2
            
        if room_height < self.screen_height:
            self.y = -(self.screen_height - room_height) / 2