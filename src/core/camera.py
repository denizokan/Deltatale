class Camera:
    """For tracking the player."""
    def __init__(self, main_game):
        self.game = main_game

        self.x = 0
        self.y = 0
        self.screen_width = self.game.constants.WIDTH
        self.screen_height = self.game.constants.HEIGHT

    
    def update(self):
        """Updates the camera x, y."""
        room_width = self.game.current_room.bg_image.width()
        room_height = self.game.current_room.bg_image.height()

        target_x = self.game.player.x - (self.screen_width / 2)
        target_y = self.game.player.y - (self.screen_height / 2)

        max_scroll_x = room_width - self.screen_width
        max_scroll_y = room_height - self.screen_height
        
        self.x = max(0, min(target_x, max_scroll_x))
        self.y = max(0, min(target_y, max_scroll_y))

        if room_width < self.screen_width:
            self.x = -(self.screen_width - room_width) / 2
            
        if room_height < self.screen_height:
            self.y = -(self.screen_height - room_height) / 2