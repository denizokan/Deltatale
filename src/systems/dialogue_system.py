import pygame
from random import uniform
from pygame import mixer
from src.core.constants import Constants, Color
from src.core.enums import Action, TextSound, Portraits

class DialogueSystem:
    """This class is used for rendering text."""

    def __init__(self, asset_manager):
        self.asset_manager = asset_manager

        self.is_active = False
        self.is_battle = False
        self.line_spacing = 35

        self.cursor_y = 0
        self.token_index = 0
        self.current_color = Color.WHITE
        self.current_font = "dtm_mono_26"
        self.portrait_image = None
        self.typewriter_delay = Constants.DEFAULT_TYPEWRITER_TIMER
        self.is_shaking = False
        self.shake_intensity = 0

        self.text_coords = (0, 0)
        self.og_text_coords = (0, 0)

        self.tokenized_text = None

        self.current_page = 0
        self.visible_char_count = 0
        self.typewriter_timer = Constants.DEFAULT_TYPEWRITER_TIMER
        self.is_line_complete = False

        self.actors = None
        self.visible_characters = []


    def get_box_rect(self, page_data):
        """Calculates starting coordinates based on mode."""
        pos = page_data.get("pos", "bottom")

        image_coords = None
        fill = None
        outline = None
        width = 0

        if self.is_battle:
            self.line_spacing = 30
            x1, x2 = 10, Constants.WIDTH - 10
            y1, y2 = Constants.HEIGHT - 125, Constants.HEIGHT
        else:
            self.line_spacing = 35
            if pos == "bottom":
                x1, x2 = 32, Constants.WIDTH - 32
                y1, y2 = Constants.HEIGHT - 155, Constants.HEIGHT - 15
            elif pos == "top":
                x1, x2 = 32, Constants.WIDTH - 32
                y1, y2 = 15, 155

            fill = Color.BLACK
            outline = Color.WHITE
            width = 6

        if page_data.get("face") != None:
            self.portrait_image = self.asset_manager.get_image(Portraits[page_data["face"]].value)
            image_coords = (x1 + 25, y1 + 17)
            text_coords = (x1 + 140, y1 + 13)
        else:
            text_coords = (x1 + 25, y1 + 13)

        return {"box_bounds": (x1, y1, x2 - x1, y2 - y1), "image_coords": image_coords, "text_coords": text_coords, "fill": fill, "outline": outline, "width": width}


    def start_dialogue(self, text, interaction_index=0, actors=None, on_complete=None, is_battle=False):
        """Freezes the player inputs and starts displaying dialogue."""
        if self.is_active: raise RuntimeError("Cannot start a new dialogue because another one is already being shown.")

        # Reset old variables
        self.close_dialogue()

        self.is_battle = is_battle

        if isinstance(text, dict):
            self.text = [text]
        elif isinstance(text, list) and len(text) > 0 and isinstance(text[0], list):
            clamped_index = min(interaction_index, len(text) - 1)
            self.text = text[clamped_index]
        else:
            self.text = text

        self.actors = actors
        self.on_complete_callback = on_complete

        self.load_page(0)

        self.is_active = True


    def load_page(self, index):
        page_data = self.text[index]
        self.close_dialogue()

        current_speaker = page_data.get("speaker", "NONE")

        if self.actors:
            for actor, interactable in self.actors.items():
                if current_speaker == actor:
                    interactable["is_speaking"] = True
                else:
                    interactable["is_speaking"] = False

        self.talk_sound = self.asset_manager.get_sfx(self._get_sound_path(TextSound[page_data["sound"]]))
        self.box_info = self.get_box_rect(page_data)

        self.visible_char_count = 0
        self.cursor_y = 0
        self.og_text_coords = self.text_coords
        self.token_index = 0
        self.current_color = Color.WHITE
        self.current_font = "dtm_mono_26"
        self.typewriter_delay = Constants.DEFAULT_TYPEWRITER_TIMER
        self.is_shaking = False
        self.shake_intensity = 0
        self.shaking_text_ids = []
        self.tokenized_text = self._tokenizer(page_data["dialogue"])


    def handle_input(self, input_mgr):
        """Handles player input if a text box is active."""
        if input_mgr.is_just_pressed(Action.CONFIRM):
            if not self.is_line_complete: return

            self.current_page += 1
            self.close_dialogue()
            if self.current_page >= len(self.text):
                self.close_dialogue(isDone=True)
                return

            self.load_page(self.current_page)

        if input_mgr.is_just_pressed(Action.CANCEL):
            if self.is_line_complete: return
            for token in self.tokenized_text[self.token_index:]:
                if token["type"] == "skip": return
            self.is_line_complete = True
            self._print_remaining_text()
            self.talk_sound.play()


    def update(self):
        """Updates every game tick to write text on the screen."""
        if not self.is_active: return

        if self.is_line_complete: return

        self.typewriter_timer -= 1
        if self.typewriter_timer <= 0:

            while self.tokenized_text[self.token_index]["type"] != "char":
                token = self.tokenized_text[self.token_index]
                
                if token["type"] == "color":
                    self.current_color = token["value"]
                elif token["type"] == "font":
                    self.current_font = token["value"]
                elif token["type"] == "shake":
                    self.shake_intensity = float(token["value"])
                    self.is_shaking = (self.shake_intensity > 0)
                elif token["type"] == "speed":
                    self.typewriter_delay = int(token["value"])
                elif token["type"] == "delay":
                    self.typewriter_timer = int(token["value"])
                    self.token_index += 1
                    return
                elif token["type"] == "newline":
                    self.cursor_y += 1
                    self.text_coords = (self.og_text_coords[0], self.og_text_coords[1] + (self.cursor_y * self.line_spacing))
                elif token["type"] == "skip":
                    self.current_page += 1
                    if self.current_page >= len(self.text):
                        self.close_dialogue(isDone=True)
                        return
                    
                    self.close_dialogue()
                    self.load_page(self.current_page)
                    return
                
                self.token_index += 1
                
                if self.token_index >= len(self.tokenized_text):
                    self.is_line_complete = True
                    return

            self.typewriter_timer = self.typewriter_delay

            # Print the letter
            if self.tokenized_text[self.token_index]["type"] == "char":
                self.visible_char_count += 1

                char = self.tokenized_text[self.token_index]["value"]
                x, y = self.text_coords
                self.visible_characters.append({
                    "char": char,
                    "color": self.current_color,
                    "font": self.current_font,
                    "x": x,
                    "y": y,
                    "shake_intensity": float(self.shake_intensity)
                })

                fixed_char_width = 15 
                self.text_coords = (x + fixed_char_width, self.og_text_coords[1] + (self.cursor_y * self.line_spacing))

                # Apply pauses
                if self.typewriter_delay == Constants.DEFAULT_TYPEWRITER_TIMER:
                    just_typed_char = char

                    next_char = ""
                    if self.token_index < len(self.tokenized_text) - 1:
                        for char in self.tokenized_text[self.token_index + 1:]:
                            if char["type"] == "char":
                                next_char = char["value"]
                                break

                    if just_typed_char in [",", ":", ";", ")"]:
                        self.typewriter_timer += 5
                    elif just_typed_char in [".", "!", "?"] and not next_char in [".", "?", "!", ")", '"', "'"]:
                        self.typewriter_timer += 10
                # ------------

                if char != " ":
                    self.talk_sound.fadeout(150)
                    self.talk_sound.play()

                if self.token_index == len(self.tokenized_text) - 1:
                    if self.actors:
                        for interactable in self.actors.values():
                            interactable["is_speaking"] = False
                    self.is_line_complete = True
                    return

                self.token_index += 1


    def draw(self, surface):
        """Draws current text on the screen."""
        if not self.is_active: return

        pygame.draw.rect(surface, self.box_info["fill"], self.box_info["box_bounds"])
        
        if self.box_info["outline"] is not None:
            border_rect = pygame.Rect(self.box_info["box_bounds"]).inflate(6, 6)
            pygame.draw.rect(surface, self.box_info["outline"], border_rect, self.box_info["width"])

        if hasattr(self, 'portrait_image') and self.portrait_image:
            surface.blit(self.portrait_image, self.box_info["image_coords"])
        
        for char_data in self.visible_characters:
            font_obj = self.asset_manager.get_font(char_data["font"])
            char_surface = font_obj.render(char_data["char"], False, char_data["color"])

            draw_x = self.box_info["text_coords"][0] + char_data["x"]
            draw_y = self.box_info["text_coords"][1] + char_data["y"]

            if char_data["shake_intensity"] > 0:
                draw_x += uniform(-char_data["shake_intensity"], char_data["shake_intensity"])
                draw_y += uniform(-char_data["shake_intensity"], char_data["shake_intensity"])

            char_rect = char_surface.get_rect(center=(draw_x, draw_y))
            surface.blit(char_surface, char_rect)


    def _print_remaining_text(self):
        """This function is called when [X] key is pressed, prints the rest of the text instantly."""
        for value in self.tokenized_text[self.token_index:]:
            is_command = False
            if value["type"] == "color":
                self.current_color = value["value"]
                is_command = True
            
            if value["type"] == "font":
                self.current_font = value["value"]
                is_command = True
            
            if value["type"] == "shake":
                self.shake_intensity = float(value["value"])
                if self.shake_intensity > 0: self.is_shaking = True
                else: self.is_shaking = False
                is_command = True
            
            # Print the letter
            if value["type"] == "newline":
                self.cursor_y += 1
                self.text_coords = (self.og_text_coords[0], self.og_text_coords[1] + (self.cursor_y * self.line_spacing))
                is_command = True
            
            if is_command:
                self.token_index += 1
            
            if value["type"] == "char":
                self.visible_char_count += 1
            
                char = value["value"]
                x, y = self.text_coords
                self.visible_characters.append({
                    "char": char,
                    "color": self.current_color,
                    "font": self.current_font,
                    "x": x,
                    "y": y,
                    "shake_intensity": float(self.shake_intensity)
                })
            
                fixed_char_width = 15
                self.text_coords = (x + fixed_char_width, self.og_text_coords[1] + (self.cursor_y * self.line_spacing))
            
                if self.token_index == len(self.tokenized_text) - 1:
                    if self.actors:
                        for interactable in self.actors.values():
                            interactable["is_speaking"] = False
                    self.is_line_complete = True
                    break
            
                self.token_index += 1


    def close_dialogue(self, isDone=False):
        """Cleans up and closes the dialogue box. If passed True, unfreezes keyboard inputs."""
        self.visible_characters.clear()

        self.cursor_y = 0
        self.token_index = 0
        self.current_color = Color.WHITE
        self.current_font = "dtm_mono_26"
        self.portrait_image = None
        self.typewriter_delay = Constants.DEFAULT_TYPEWRITER_TIMER
        self.is_shaking = False
        self.shake_intensity = 0

        self.tokenized_text = None
        self.text_coords = (0, 0)
        self.og_text_coords = (0, 0)

        self.visible_char_count = 0
        self.typewriter_timer = Constants.DEFAULT_TYPEWRITER_TIMER
        self.is_line_complete = False

        if self.actors:
            for interactable in self.actors.values():
                interactable["is_speaking"] = False

        if isDone:
            self.actors = None
            self.current_page = 0
            self.is_active = False
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


    def _tokenizer(self, text_string):
        """
        Parses dialogue strings containing rich-text formatting tags into a list of sequential action tokens.

        This parser reads a raw string and separates printable characters from command tags. 
        It enables Undertale/Deltarune style text effects such as inline color changes, 
        dynamic typing delays, custom fonts, and animated text effects (like shaking).

        Supported Formatting Tags:
        --------------------------
        Color:
        \\c[color_name] : Changes the color of all following characters. 
                        Example: "\\c[red]" or "\\c[yellow]". Use "\\c[white]" to reset.

        Delay / Pauses:
        \\d[frames]    : Pauses the typewriter effect for the specified number of game frames.
                        Example: "Wait...\\d[30] who are you?"

        Typing Speed:
        \\sp[frames]   : Changes the typing speed (frames to wait between each character).
                        Example: "\\sp[1]" (fast) or "\\sp[5]" (slow).

        Font:
        \\f[font_name] : Changes the font of all following characters.
                        Example: "\\f[Papyrus]" or "\\f[Determination Mono]".

        Shake Effect:
        \\s[intensity] : Causes all following characters to shake randomly on screen. 
                        The 'intensity' integer determines the maximum pixel offset.
                        Example: "\\s[2]" (shake by 2 pixels). Use "\\s[0]" to disable.

        Newlines:
        \\n            : Moves the virtual cursor to the beginning of the next line.

        Skips:
        \\sk           : Skips to the next dialogue automatically without player input.

        Example Usage:
        --------------
        Raw String:
            "* \\c[red]Red\\c[white], and a \\d[30]delay!"

        Conceptual Token Output:
            ```
            [
                {"type": "char", "value": "*"},
                {"type": "char", "value": " "},
                {"type": "color", "value": "red"},
                {"type": "char", "value": "R"},
                {"type": "char", "value": "e"},
                {"type": "char", "value": "d"},
                {"type": "color", "value": "white"},
                {"type": "char", "value": ","},
                {"type": "char", "value": " "},
                ...
                {"type": "delay", "value": 30},
                {"type": "char", "value": "d"},
                ...
            ]
            ```
        """

        cmds = {
            "c": "color",
            "d": "delay",
            "sp": "speed",
            "f": "font",
            "s": "shake"
        }

        output = []
        text_list = list(text_string)
        commands = []

        for index, char in enumerate(text_list):
            if char == "\\" and text_list[index + 1] == "n": # Newline
                commands.append({
                    "command": "newline",
                    "index": (index, index + 1),
                    "value": None
                })

            elif char == "\\" and "".join([text_list[index + 1], text_list[index + 2]]) == "sk": # Skip
                commands.append({
                    "command": "skip",
                    "index": (index, index + 2),
                    "value": None
                })

            elif char == "\\":
                command_name = ("".join(text_list[index + 1:])).split("[")[0]
                if command_name in cmds.keys():
                    value = []

                    cursor = index + len(command_name) + 2
                    for val in text_list[cursor:]:
                        if val == "]":
                            break
                        cursor += 1
                        value.append(val)


                    commands.append({
                        "command": cmds.get(command_name),
                        "index": (index, cursor),
                        "value": "".join(value)
                    })

        skip_indexes = []
        for command in commands:
            skip_indexes.append(command["index"])

        def check_cmd(index):
            for i, cursor_pos in enumerate(skip_indexes):
                if cursor_pos[0] <= index <= cursor_pos[1]:
                    return {
                        "type": commands[i]["command"],
                        "value": commands[i]["value"]
                    }

        # Tokenization
        for index, letter in enumerate(text_list):
            func_output = check_cmd(index)
            if func_output == None:
                output.append({
                    "type": "char",
                    "value": letter
                })
            else:
                output.append(func_output)
                if index > 0 and output[-2] == func_output: output.pop(-1)

        return output