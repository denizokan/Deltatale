from src.events.flowey_intro import FloweyIntroCutscene

class CutsceneManager:
    """This class acts as a general manager for cutscene and forwards
    specific cutscenes to their respective class."""

    def __init__(self, main_game):
        self.game = main_game
        self.active_cutscene = None

        self.cutscene_registry = {
            "flowey_first_interaction": FloweyIntroCutscene
        }