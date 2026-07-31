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
    BATTLE = 3
    GAMEOVER = 4

class Character(Enum):
    """Contains all characters. Check with Character.VALUE"""

    KRIS = auto()
    SUSIE = auto()
    FLOWEY = auto()
    TORIEL = auto()

class Portraits(Enum):
    """Contains character portraits and their sprite location keys. Check with Portraits.VALUE"""

    # Susie
    SUSIE_NEUTRAL = "susie_neutral"
    SUSIE_SMILE = "susie_smile"
    SUSIE_SMIRK = "susie_smirk"
    SUSIE_MANIAC = "susie_maniac"
    SUSIE_GRIN = "susie_grin"
    SUSIE_SWEAT_NEUTRAL = "susie_sweat_neutral"
    SUSIE_SWEAT_SMILE = "susie_sweat_smile"
    SUSIE_SWEAT_MANIAC = "susie_sweat_maniac"
    SUSIE_ANNOYED = "susie_annoyed"
    SUSIE_SWEAT_MANIAC_NO_EYE = "susie_sweat_maniac_no_eye"
    SUSIE_PISSED = "susie_pissed"
    SUSIE_ROAR = "susie_roar"
    SUSIE_ROAR_2 = "susie_roar2"
    SUSIE_LOOK_AWAY = "susie_look_away"
    SUSIE_SMILE_SIDE = "susie_smile_side"
    SUSIE_UNIMPRESSED = "susie_unimpressed"
    SUSIE_UNIMPRESSED_2 = "susie_unimpressed2"
    SUSIE_HAPPY_TEETH = "susie_happy_teeth"
    SUSIE_UNIMPRESSED_SMIRK = "susie_unimpressed_smirk"
    SUSIE_UNIMPRESSED_SMIRK_2 = "susie_unimpressed_smirk2"
    SUSIE_UNHAPPY_SMIRK = "susie_unhappy_smirk"
    SUSIE_DERANGED = "susie_deranged"
    SUSIE_AWKWARD = "susie_awkward"
    SUSIE_HAPPY = "susie_happy"
    SUSIE_SMIRK_AWKWARD = "susie_smirk_awkward"

    # Flowey
    FLOWEY_NEUTRAL = "flowey_neutral"
    FLOWEY_SMILE = "flowey_smile"
    FLOWEY_WINK = "flowey_wink"
    FLOWEY_SMILE_ANNOYED = "flowey_smile_annoyed"
    FLOWEY_PISSED = "flowey_pissed"
    FLOWEY_ANGRY = "flowey_angry"
    FLOWEY_WORRIED = "flowey_worried"
    FLOWEY_SAD = "flowey_sad"
    FLOWEY_SCARED = "flowey_scared"
    FLOWEY_SCARY = "flowey_scary"
    FLOWEY_MANIAC = "flowey_maniac"
    FLOWEY_MANIAC_2 = "flowey_maniac2"


class TextSound(Enum):
    """Contains character sounds location keys. Check with TextSound.VALUE"""
    GENERIC = "snd_txt1"
    SUSIE = "snd_txtsus"
    #SUSIE_LAUGH = auto()
    #SUSIE_ROAR = auto()
    #SUSIE_SURPRISE = auto()

    FLOWEY = "snd_floweytalk1"
    FLOWEY_EVIL = "snd_floweytalk2"

    TORIEL = "snd_txttor"

class Interactable(Enum):
    """Contains all interactables. Check with Interactable.VALUE"""

    SAVE_POINT = "SAVE_POINT"
    NPC = "NPC"