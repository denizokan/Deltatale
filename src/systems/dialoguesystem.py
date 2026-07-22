from pygame import mixer
from src.core.enums import Action, TextSound

class DialogueSystem:
    """This class is used for rendering text."""

    def __init__(self, main_game):
        self.game = main_game

        self.is_active = False
        self.current_page = 0
        self.visible_char_count = 0
        self.typewriter_timer = 2
        self.is_line_complete = False

        self.active_text_elements = []


    def draw_text_box(self, pos):
        if pos == "bottom":
            x1, x2 = 40, self.game.constants.WIDTH - 40
            y1, y2 = self.game.constants.HEIGHT - 240, self.game.constants.HEIGHT - 40
        elif pos == "top":
            x1, x2 = 40, self.game.constants.WIDTH - 40
            y1, y2 = 40, 240

        self.text_box = self.game.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="white", width=4)
        self.text_id = self.game.canvas.create_text(x1 + 20, y1 + 20, text="", fill="white", font=("Determination Mono", 24, "normal"), anchor="nw")
        self.active_text_elements.extend([self.text_box, self.text_id])


    def start_dialogue(self, text, sound, pos="bottom", on_complete=None):
        """Freezes the player inputs and starts displaying dialogue."""
        if self.is_active: raise RuntimeError("Cannot start a new dialogue because another one is already being shown.")

        # Reset old variables
        self.current_page = 0
        self.visible_char_count = 0
        self.typewriter_timer = 2
        self.is_line_complete = False

        self.game.current_room.is_paused = True
        self.is_active = True
        self.text = text
        self.sound_path = self._get_sound_path(sound)
        self.talk_sound = mixer.Sound(file=self.sound_path)
        self.on_complete_callback = on_complete

        self.draw_text_box(pos)


    def handle_input(self, input_mgr):
        """Handles player input if a text box is active."""
        if input_mgr.is_just_pressed(Action.CONFIRM):
            if not self.is_line_complete: return

            self.current_page += 1
            if self.current_page >= len(self.text):
                self.close_dialogue()
                return

            self.visible_char_count = 0
            self.typewriter_timer = 2
            self.is_line_complete = False
            self.game.canvas.itemconfig(self.text_id, text="")

        if input_mgr.is_just_pressed(Action.CANCEL):
            if self.is_line_complete: return
            self.is_line_complete = True
            current_line = self.text[self.current_page]
            self.visible_char_count = len(current_line)
            self.typewriter_timer = 2
            self.game.canvas.itemconfig(self.text_id, text=current_line)
            self.talk_sound.play()


    def update(self):
        """Updates every game tick to write text on the screen."""
        if not self.is_active: return
        if self.is_line_complete: return

        self.typewriter_timer -= 1
        if self.typewriter_timer <= 0:
            self.visible_char_count += 1
            self.typewriter_timer = 2

            current_line = self.text[self.current_page]
            self.game.canvas.itemconfig(self.text_id, text=current_line[0:self.visible_char_count])

            if current_line[self.visible_char_count - 1] != " ":
                self.talk_sound.play()

            if self.visible_char_count == len(current_line):
                self.is_line_complete = True


    def close_dialogue(self):
        """Cleans up and closes the dialogue box."""
        for element in self.active_text_elements:
            self.game.canvas.delete(element)

        self.is_active = False
        self.game.current_room.is_paused = False
        if self.on_complete_callback != None:
            self.on_complete_callback()


    def _get_sound_path(self, sound):
        """
        Returns the sound file path for the specified sound.
        """
        sound_folder = "sounds/text_sounds/"
        if sound == TextSound.GENERIC:
            return sound_folder + "snd_text1.wav"
        if sound == TextSound.SUSIE:
            return sound_folder + "snd_txtsus.wav"
        if sound == TextSound.FLOWEY:
            return sound_folder + "snd_floweytalk1.wav"
        if sound == TextSound.FLOWEY:
            return sound_folder + "snd_txttor.wav"