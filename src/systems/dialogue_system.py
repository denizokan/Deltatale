from pygame import mixer
from tkinter import PhotoImage
from src.core.enums import Action, TextSound, Portraits

class DialogueSystem:
    """This class is used for rendering text."""

    def __init__(self, main_game):
        self.game = main_game

        self.is_active = False
        self.current_page = 0
        self.visible_char_count = 0
        self.typewriter_timer = self.game.constants.DEFAULT_TYPEWRITER_TIMER
        self.is_line_complete = False

        self.active_text_elements = []


    def draw_text_box(self, page_data):
        """Draws a blank text box and creates an empty text canvas object."""
        pos = page_data["pos"]
        if pos == "bottom":
            x1, x2 = 32, self.game.constants.WIDTH - 32
            y1, y2 = self.game.constants.HEIGHT - 155, self.game.constants.HEIGHT - 15
        elif pos == "top":
            x1, x2 = 32, self.game.constants.WIDTH - 32
            y1, y2 = 15, 155

        self.text_box = self.game.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="white", width=6)
        if page_data["face"] != None:
            self.portrait_sprite = PhotoImage(file=Portraits[page_data["face"]].value).zoom(2)
            self.portrait_id = self.game.canvas.create_image(x1 + 25, y1 + 17, image=self.portrait_sprite, anchor="nw")
            self.text_id = self.game.canvas.create_text(x1 + 140, y1 + 13, text="", fill="white", font=("Determination Mono", 26, "normal"), anchor="nw")
            self.active_text_elements.extend([self.text_box, self.portrait_id, self.text_id])
        else:
            self.text_id = self.game.canvas.create_text(x1 + 25, y1 + 13, text="", fill="white", font=("Determination Mono", 26, "normal"), anchor="nw")
            self.active_text_elements.extend([self.text_box, self.text_id])


    def start_dialogue(self, text, interaction_index=0, on_complete=None):
        """Freezes the player inputs and starts displaying dialogue."""
        if self.is_active: raise RuntimeError("Cannot start a new dialogue because another one is already being shown.")

        # Reset old variables
        self.close_dialogue()

        if isinstance(text, dict):
            self.text = [text]
        elif isinstance(text, list) and len(text) > 0 and isinstance(text[0], list):
            clamped_index = min(interaction_index, len(text) - 1)
            self.text = text[clamped_index]
        else:
            self.text = text

        self.on_complete_callback = on_complete

        self.load_page(0)

        self.game.current_room.is_paused = True
        self.is_active = True


    def load_page(self, index):
        page_data = self.text[index]
        self.close_dialogue()
        self.talk_sound = mixer.Sound(file=self._get_sound_path(TextSound[page_data["sound"]]))
        self.draw_text_box(page_data)


    def handle_input(self, input_mgr):
        """Handles player input if a text box is active."""
        if input_mgr.is_just_pressed(Action.CONFIRM):
            if not self.is_line_complete: return

            self.current_page += 1
            if self.current_page >= len(self.text):
                self.close_dialogue(isDone=True)
                return

            self.close_dialogue()
            self.load_page(self.current_page)

        if input_mgr.is_just_pressed(Action.CANCEL):
            if self.is_line_complete: return
            self.is_line_complete = True
            current_line = self.text[self.current_page]["dialogue"]
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
            self.typewriter_timer = self.game.constants.DEFAULT_TYPEWRITER_TIMER

            current_line = self.text[self.current_page]["dialogue"]
            self.game.canvas.itemconfig(self.text_id, text=current_line[0:self.visible_char_count])

            just_typed_char = current_line[self.visible_char_count - 1]
            if self.visible_char_count < len(current_line):
                next_char = current_line[self.visible_char_count]
            else:
                next_char = ""

            if just_typed_char in [",", ":", ";", ")"]:
                self.typewriter_timer += 5
            elif just_typed_char in [".", "!", "?"] and not next_char in [".", ")", '"', "'"]:
                self.typewriter_timer += 10

            if current_line[self.visible_char_count - 1] != " ":
                #if self.visible_char_count % 2 == 0:
                    self.talk_sound.fadeout(150)
                    self.talk_sound.play()

            if self.visible_char_count == len(current_line):
                self.is_line_complete = True


    def close_dialogue(self, isDone=False):
        """Cleans up and closes the dialogue box. If passed True, unfreezes keyboard inputs."""
        self.text_box = None
        self.text_id = None

        self.visible_char_count = 0
        self.typewriter_timer = self.game.constants.DEFAULT_TYPEWRITER_TIMER
        self.is_line_complete = False
        
        for element in self.active_text_elements:
            self.game.canvas.delete(element)
        self.active_text_elements = []

        if isDone:
            self.current_page = 0
            self.is_active = False
            self.game.current_room.is_paused = False
            if self.on_complete_callback != None:
                self.on_complete_callback()


    def _get_sound_path(self, sound):
        """
        Returns the sound file path string for the specified sound.
        Accepts both string keys ("GENERIC") and Enum members (TextSound.GENERIC).
        """
        if isinstance(sound, TextSound):
            return sound.value
            
        if isinstance(sound, str):
            return TextSound[sound].value
            
        raise ValueError(f"Invalid sound type: {sound}")