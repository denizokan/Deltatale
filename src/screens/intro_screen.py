from src.core.constants import Constants, Color
from src.core.enums import Action, Event
from src.core.events import EventBus

class IntroScreen:
    """Gets called on game launch. Shows the logo."""
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager

        self.showing_text = False
        self.frames = 0
        self.logo = asset_manager.get_image("logo")
        self.logo_pos = (Constants.WIDTH // 2, Constants.HEIGHT // 2.2)
        self.intro_sound = asset_manager.get_sfx("mus_intronoise")
        self.intro_sound.play()


    def handle_input(self, input_mgr):
        """Gets called every game tick to check for inputs."""
        if input_mgr.is_just_pressed(Action.CONFIRM):
            EventBus.emit(Event.SWITCH_TO_FILE_SELECT, True)


    def update(self):
        """Handles logic and timers."""
        if not self.showing_text:
            self.frames += 1
            if self.frames >= Constants.FPS * 3:
                self.showing_text = True


    def draw(self, screen):
        """Draws the intro screen to the screen every frame."""
        logo_rect = self.logo.get_rect(center=(Constants.WIDTH // 2, Constants.HEIGHT // 2.2))
        screen.blit(self.logo, logo_rect)

        if self.showing_text:
            intro_font = self.asset_manager.get_font("dtm_sans_20")
            intro_surf = intro_font.render("Press [Z] or [ENTER]", False, Color.GRAY)
            text_rect = intro_surf.get_rect(center=(Constants.WIDTH // 2, Constants.HEIGHT // 2 + 120))
            screen.blit(intro_surf, text_rect)