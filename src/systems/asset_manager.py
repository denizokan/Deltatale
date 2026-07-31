import os
import re
import json
from pygame import image, transform, font, freetype, mixer
from src.core.enums import Event
from src.core.events import EventBus

class AssetManager:
    """This class loads all the game assets on startup and holds them on system RAM."""

    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.sfx = {}

        EventBus.subscribe(Event.PLAY_SOUND, self.play_sfx)
        EventBus.subscribe(Event.PLAY_MUSIC, self.play_music)
        EventBus.subscribe(Event.STOP_SOUND, self.stop_sfx)

    # Setter Methods
    def load_all(self):
        """The manifest. Calls the setters to load files into RAM."""

        # Load Images
        self.load_image("logo", "assets/images/logo/LOGO.png", scaling=0.75)
        self.load_characters()
        self.load_all_sprites("assets/images/sprites", scaling=2)
        self.load_all_rooms("assets/images/tilesets", scaling=2)
        self.load_image("spr_soul", "assets/images/sprites/spr_soul.png", scaling=1)
        self.load_image("spr_monster_soul", "assets/images/sprites/spr_monster_soul.png", scaling=1)

        # Load Fonts
        self.load_font("dtm_sans_16", "assets/fonts/DTM-Sans.otf", 16)
        self.load_font("dtm_sans_20", "assets/fonts/DTM-Sans.otf", 20)
        self.load_font("dtm_sans_24", "assets/fonts/DTM-Sans.otf", 24)
        self.load_font("dtm_sans_26", "assets/fonts/DTM-Sans.otf", 26)
        self.load_font("dtm_sans_36", "assets/fonts/DTM-Sans.otf", 36)
        self.load_font("dtm_mono_26", "assets/fonts/DTM-Mono.otf", 26)

        # Load SFX
        self.load_all_sfx("assets/sfx/sound_effects")
        self.load_all_sfx("assets/sfx/text_sounds")
        self.load_sfx("menu_theme", "assets/sfx/musics/menu_theme.mp3")


    def load_characters(self):
        """Loads all Kris & Susie sprites to memory."""
        for char in ["kris", "susie"]:
            char_dict = {
                "down": [],
                "up": [],
                "left": [],
                "right": []
            }

            for direction in char_dict.keys():
                first_letter = list(direction)[0]
                for frame in range(4):
                    path = f"assets/images/sprites/characters/{char}/walk/spr_{char}{first_letter}_{frame}.png"
                    loaded_img = image.load(path).convert_alpha()
                    scaled_image = transform.scale_by(loaded_img, 2)
                    char_dict[direction].append(scaled_image)

            self.images[char] = char_dict


    def load_all_sprites(self, root_folder="assets/images/sprites", scaling=2):
        pattern = re.compile(r"(.+)_(\d+)\.png$")

        for directory_path, directory_names, file_names in os.walk(root_folder):
            scale = scaling
            for file_name in file_names:
                if not file_name.endswith(".png"):
                    continue

                if "walk" in directory_path: # Skip Kris/Susie walking sprites
                    continue

                if "bullets" in directory_path:
                    scale = 1
                
                full_path = os.path.join(directory_path, file_name)
                loaded_img = image.load(full_path).convert_alpha()
                scaled_img = transform.scale_by(loaded_img, scale)
                
                match = pattern.match(file_name)
                
                if match:
                    base_name = match.group(1)
                    frame_index = int(match.group(2))
                    
                    if base_name not in self.images:
                        self.images[base_name] = []

                    while len(self.images[base_name]) <= frame_index:
                        self.images[base_name].append(None)
                    self.images[base_name][frame_index] = scaled_img
                    
                else:
                    base_name = file_name[:-4]
                    self.images[base_name] = scaled_img


    def load_all_rooms(self, root_folder="assets/images/tilesets", scaling=2):
        for directory_path, directory_names, file_names in os.walk(root_folder):
            scale = scaling
            for file_name in file_names:
                if not file_name.endswith(".png"):
                    continue

                full_path = os.path.join(directory_path, file_name)
                loaded_img = image.load(full_path).convert_alpha()
                scaled_img = transform.scale_by(loaded_img, scale)
                base_name = file_name[:-4]
                self.images[base_name] = scaled_img


    def load_all_sfx(self, root_folder="assets/sfx/sound_effects"):
        for directory_path, directory_names, file_names in os.walk(root_folder):
            for file_name in file_names:
                if not file_name.endswith((".ogg", ".wav", ".mp3")):
                    continue

                full_path = os.path.join(directory_path, file_name)
                loaded_sound = mixer.Sound(full_path)
                base_name = file_name[:-4]
                self.sfx[base_name] = loaded_sound


    def load_image(self, name, path, scaling=2):
        """Loads an image from the hard disk and stores the image in self.images class variable."""
        loaded_img = image.load(path).convert_alpha()
        scaled_img = transform.scale_by(loaded_img, scaling)
        self.images[name] = scaled_img


    def load_font(self, name, path, size):
        """Loads a font from the hard disk and stores the font in self.fonts class variable."""
        loaded_font = font.Font(path, size)
        self.fonts[name] = loaded_font


    def load_sfx(self, name, path):
        """Loads a sound from the hard disk and stores the sound in self.sfx class variable."""
        loaded_sound = mixer.Sound(path)
        self.sfx[name] = loaded_sound


    # Getter Methods
    def get_image(self, name):
        """Returns the image object with name."""
        if name not in self.images.keys():
            print(f"Unknown image: {name}")
            return None

        return self.images[name]


    def get_font(self, name):
        """Returns the font object with name."""
        if name not in self.fonts.keys():
            print(f"Unknown font: {name}")
            return None
        
        return self.fonts[name]


    def get_sfx(self, name):
        """Returns the sound object with name."""
        if name not in self.sfx.keys():
            print(f"Unknown sound: {name}")
            return None

        return self.sfx[name]


    def get_room_data(self, room_id):
        try:
            with open("data/rooms/" + room_id + ".json", "r") as file:
                room_data = json.load(file)
            return room_data
        except Exception as e:
            print(f"Warning: Could not read room data: {e}")


    # Event Bus Methods
    def play_sfx(self, sound_name):
        """Event bus method: Plays the given sound once."""
        sound = self.get_sfx(sound_name)
        if sound:
            sound.play()


    def play_music(self, sound_name):
        """Event bus method: Loops the given music track indefinitely."""
        sound = self.get_sfx(sound_name)
        if sound:
            sound.play(-1)


    def stop_sfx(self, data):
        """
        Event bus method: Stops the given sound. 
        Accepts string ('snd_power') or list/tuple (['snd_power', 100]).
        """
        fadeout = 0
        if isinstance(data, (list, tuple)):
            sound_name = data[0]
            if len(data) > 1:
                fadeout = data[1]
        else:
            sound_name = data
        
        sound = self.get_sfx(sound_name)
        if sound:
            if fadeout > 0:
                sound.fadeout(fadeout)
            else:
                sound.stop()