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
    """Contains character portraits. Check with Portraits.VALUE"""
    _portraits_folder: ClassVar[str] = "sprites/characters/susie/portraits"

    # Susie
    SUSIE_NEUTRAL = f"{_portraits_folder}/spr_face_s0_0.png"
    SUSIE_SMILE = f"{_portraits_folder}/spr_face_s1_0.png"
    SUSIE_SMIRK = f"{_portraits_folder}/spr_face_s2_0.png"
    SUSIE_MANIAC = f"{_portraits_folder}/spr_face_s3_0.png"
    SUSIE_GRIN = f"{_portraits_folder}/spr_face_s4_0.png"
    SUSIE_SWEAT_NEUTRAL = f"{_portraits_folder}/spr_face_s5_0.png"
    SUSIE_SWEAT_SMILE = f"{_portraits_folder}/spr_face_s6_0.png"
    SUSIE_SWEAT_MANIAC = f"{_portraits_folder}/spr_face_s7_0.png"
    SUSIE_ANNOYED = f"{_portraits_folder}/spr_face_s8_0.png"
    SUSIE_SWEAT_MANIAC_NO_EYE = f"{_portraits_folder}/spr_face_s9_0.png"
    SUSIE_PISSED = f"{_portraits_folder}/spr_face_sA_0.png"
    SUSIE_ROAR = f"{_portraits_folder}/spr_face_sB_0.png"
    SUSIE_ROAR2 = f"{_portraits_folder}/spr_face_sB_1.png"
    SUSIE_LOOK_AWAY = f"{_portraits_folder}/spr_face_sC_0.png"
    SUSIE_SMILE_SIDE = f"{_portraits_folder}/spr_face_sD_0.png"
    SUSIE_UNIMPRESSED = f"{_portraits_folder}/spr_face_susie_alt_1.png"
    SUSIE_HAPPY_TEETH = f"{_portraits_folder}/spr_face_susie_alt_2.png"
    SUSIE_UNIMPRESSED_SMIRK = f"{_portraits_folder}/spr_face_susie_alt_3.png"
    SUSIE_UNHAPPY_SMIRK = f"{_portraits_folder}/spr_face_susie_alt_4.png"
    SUSIE_DERANGED = f"{_portraits_folder}/spr_face_susie_alt_5.png"
    SUSIE_AWKWARD = f"{_portraits_folder}/spr_face_susie_alt_6.png"
    SUSIE_HAPPY = f"{_portraits_folder}/spr_face_susie_alt_7.png"
    SUSIE_SMIRK_AWKWARD = f"{_portraits_folder}/spr_face_susie_alt_8.png"
    SUSIE_UNIMPRESSED_SMIRK2 = f"{_portraits_folder}/spr_face_susie_alt_9.png"



class TextSound(Enum):
    """Contains character sounds. Check with TextSound.VALUE"""
    _sound_folder: ClassVar[str] = "sounds/text_sounds"

    GENERIC = f"{_sound_folder}/snd_txt1.wav"
    SUSIE = f"{_sound_folder}/snd_txtsus.wav"
    #SUSIE_LAUGH = auto()
    #SUSIE_ROAR = auto()
    #SUSIE_SURPRISE = auto()
    FLOWEY = f"{_sound_folder}/snd_floweytalk1.wav"
    TORIEL = f"{_sound_folder}/snd_txttor.wav"

class Interactable(Enum):
    """Contains all interactables. Check with Interactable.VALUE"""

    SAVE_POINT = "SAVE_POINT"