import os
import re
from pygame import image, font, mixer

class AssetManager:
    """This class loads all the game assets on startup and holds them on system RAM."""

    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.sfx = {}

    # Setter Methods
    def load_all(self):
        """The manifest. Calls the setters to load files into RAM."""

        # Load Images
        self.load_image("logo", "assets/images/logo/LOGO.png")
        self.load_characters()
        self.load_all_sprites("assets/images/sprites")

        # Load Fonts
        self.load_font("dtm_sans_16", "assets/fonts/Determination Sans.ttf", 16)
        self.load_font("dtm_sans_20", "assets/fonts/Determination Sans.ttf", 20)
        self.load_font("dtm_sans_24", "assets/fonts/Determination Sans.ttf", 24)

        # Load SFX
        self.load_sfx("intro_noise", "assets/sfx/sound_effects/mus_intronoise.ogg")


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
                    char_dict[direction].append(loaded_img)

            self.images[char] = char_dict


    def load_all_sprites(self, root_folder="assets/images/sprites"):
        pattern = re.compile(r"(.+)_(\d+)\.png$")

        for directory_path, directory_names, file_names in os.walk(root_folder):
            for file_name in file_names:
                if not file_name.endswith(".png"):
                    continue

                if "walk" in directory_path: # Skip Kris/Susie walking sprites
                    continue
                
                full_path = os.path.join(directory_path, file_name)
                loaded_img = image.load(full_path).convert_alpha()
                
                match = pattern.match(file_name)
                
                if match:
                    base_name = match.group(1)
                    frame_index = int(match.group(2))
                    
                    if base_name not in self.images:
                        self.images[base_name] = []

                    while len(self.images[base_name]) <= frame_index:
                        self.images[base_name].append(None)
                    self.images[base_name][frame_index] = loaded_img
                    
                else:
                    base_name = file_name[:-4]
                    self.images[base_name] = loaded_img


    def load_image(self, name, path):
        """Loads an image from the hard disk and stores the image in self.images class variable."""
        loaded_image = image.load(path).convert_alpha()
        self.images[name] = loaded_image


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