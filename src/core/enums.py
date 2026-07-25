from enum import Enum, auto
from typing import ClassVar

class Action(Enum):
    """
    All possible events that can occur while in game. Check with is_pressed(Action.STATE)
    """

    # Menu
    CONFIRM = 1
    CANCEL = 2
    MENU = 3
    FULLSCREEN = 4
    QUIT = 5

    # Movement
    UP = 6
    DOWN = 7
    LEFT = 8
    RIGHT = 9

    DEBUG = 10

class GameState(Enum):
    """
    All possible game states. Check with GameState.VALUE
    """

    INTRO = 0
    FILE_SELECT = 1
    PLAYING = 2
    CUTSCENE = 3
    BATTLE = 4
    GAMEOVER = 5

class Character(Enum):
    """Contains all characters. Check with Character.VALUE"""

    KRIS = auto()
    SUSIE = auto()
    FLOWEY = auto()
    TORIEL = auto()

class Portraits(Enum):
    """Contains character portraits. Check with Portraits.VALUE"""
    _portraits_folder: ClassVar[str] = "sprites/characters"

    # Susie
    SUSIE_NEUTRAL = f"{_portraits_folder}/susie/portraits/susie_neutral.png"
    SUSIE_SMILE = f"{_portraits_folder}/susie/portraits/susie_smile.png"
    SUSIE_SMIRK = f"{_portraits_folder}/susie/portraits/susie_smirk.png"
    SUSIE_MANIAC = f"{_portraits_folder}/susie/portraits/susie_maniac.png"
    SUSIE_GRIN = f"{_portraits_folder}/susie/portraits/susie_grin.png"
    SUSIE_SWEAT_NEUTRAL = f"{_portraits_folder}/susie/portraits/susie_sweat_neutral.png"
    SUSIE_SWEAT_SMILE = f"{_portraits_folder}/susie/portraits/susie_sweat_smile.png"
    SUSIE_SWEAT_MANIAC = f"{_portraits_folder}/susie/portraits/susie_sweat_maniac.png"
    SUSIE_ANNOYED = f"{_portraits_folder}/susie/portraits/susie_annoyed.png"
    SUSIE_SWEAT_MANIAC_NO_EYE = f"{_portraits_folder}/susie/portraits/susie_sweat_maniac_no_eye.png"
    SUSIE_PISSED = f"{_portraits_folder}/susie/portraits/susie_pissed.png"
    SUSIE_ROAR = f"{_portraits_folder}/susie/portraits/susie_roar.png"
    SUSIE_ROAR_2 = f"{_portraits_folder}/susie/portraits/susie_roar_2.png"
    SUSIE_LOOK_AWAY = f"{_portraits_folder}/susie/portraits/susie_look_away.png"
    SUSIE_SMILE_SIDE = f"{_portraits_folder}/susie/portraits/susie_smile_side.png"
    SUSIE_UNIMPRESSED = f"{_portraits_folder}/susie/portraits/susie_unimpressed.png"
    SUSIE_UNIMPRESSED_2 = f"{_portraits_folder}/susie/portraits/susie_unimpressed_2.png"
    SUSIE_HAPPY_TEETH = f"{_portraits_folder}/susie/portraits/susie_happy_teeth.png"
    SUSIE_UNIMPRESSED_SMIRK = f"{_portraits_folder}/susie/portraits/susie_unimpressed_smirk.png"
    SUSIE_UNIMPRESSED_SMIRK_2 = f"{_portraits_folder}/susie/portraits/susie_unimpressed_smirk_2.png"
    SUSIE_UNHAPPY_SMIRK = f"{_portraits_folder}/susie/portraits/susie_unhappy_smirk.png"
    SUSIE_DERANGED = f"{_portraits_folder}/susie/portraits/susie_deranged.png"
    SUSIE_AWKWARD = f"{_portraits_folder}/susie/portraits/susie_awkward.png"
    SUSIE_HAPPY = f"{_portraits_folder}/susie/portraits/susie_happy.png"
    SUSIE_SMIRK_AWKWARD = f"{_portraits_folder}/susie/portraits/susie_smirk_awkward.png"

    # Flowey
    FLOWEY_NEUTRAL = f"{_portraits_folder}/flowey/portraits/flowey_neutral.png"
    FLOWEY_SMILE = f"{_portraits_folder}/flowey/portraits/flowey_smile.png"
    FLOWEY_WINK = f"{_portraits_folder}/flowey/portraits/flowey_wink.png"
    FLOWEY_SMILE_ANNOYED = f"{_portraits_folder}/flowey/portraits/flowey_smile_annoyed.png"
    FLOWEY_PISSED = f"{_portraits_folder}/flowey/portraits/flowey_pissed.png"
    FLOWEY_ANGRY = f"{_portraits_folder}/flowey/portraits/flowey_angry.png"
    FLOWEY_WORRIED = f"{_portraits_folder}/flowey/portraits/flowey_worried.png"
    FLOWEY_SAD = f"{_portraits_folder}/flowey/portraits/flowey_sad.png"
    FLOWEY_SCARED = f"{_portraits_folder}/flowey/portraits/flowey_scared.png"
    FLOWEY_SCARY = f"{_portraits_folder}/flowey/portraits/flowey_scary.png"
    FLOWEY_MANIAC = f"{_portraits_folder}/flowey/portraits/flowey_maniac.png"
    FLOWEY_MANIAC_2 = f"{_portraits_folder}/flowey/portraits/flowey_maniac_2.png"


class TextSound(Enum):
    """Contains character sounds. Check with TextSound.VALUE"""
    _sound_folder: ClassVar[str] = "sounds/text_sounds"

    GENERIC = f"{_sound_folder}/snd_txt1.wav"
    SUSIE = f"{_sound_folder}/snd_txtsus.wav"
    #SUSIE_LAUGH = auto()
    #SUSIE_ROAR = auto()
    #SUSIE_SURPRISE = auto()

    FLOWEY = f"{_sound_folder}/snd_floweytalk1.wav"
    FLOWEY_EVIL = f"{_sound_folder}/snd_floweytalk2.wav"

    TORIEL = f"{_sound_folder}/snd_txttor.wav"

class Interactable(Enum):
    """Contains all interactables. Check with Interactable.VALUE"""

    SAVE_POINT = "SAVE_POINT"