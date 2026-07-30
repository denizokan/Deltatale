import json
from src.core.enums import GameState
from src.events.first_room import FirstRoomCutscene
from src.events.flowey_intro import FloweyIntroCutscene

class CutsceneManager:
    """This class acts as a general manager for cutscene and forwards
    specific cutscenes to their respective class."""

    def __init__(self, main_game):
        self.game = main_game
        self.active_cutscene = None
        self.cutscene_id = None
        self.cutscene_cls = None
        self.blocks_player = True

        self.cutscene_registry = {
            "first_room": FirstRoomCutscene,
            "flowey_first_interaction": FloweyIntroCutscene
        }


    def play_cutscene(self, cutscene_id):
        """This function is used for initilizing a cutscene."""
        if self.active_cutscene != None: raise RuntimeError("Another cutscene is already active and playing.")

        self.cutscene_cls = self.cutscene_registry.get(cutscene_id, None)
        if self.cutscene_cls == None: raise RuntimeError(f"No cutscene found with ID {cutscene_id}.")

        self.cutscene_id = cutscene_id
        self.active_cutscene = self.cutscene_cls(self.game, self)


    def update(self):
        """Runs every game tick to update cutscene timeline."""
        if self.active_cutscene == None: return

        self.active_cutscene.update()


    def stop_cutscene(self):
        """Ends the current cutscene and hands control to the player manager classes."""
        if self.active_cutscene == None and self.cutscene_cls == None: return
        self.game.flags[f"cutscene_{self.cutscene_id}_completed"] = True
        self.active_cutscene = None
        self.cutscene_id = None
        self.cutscene_cls = None


    def load_json(self, cutscene_id):
        """Loads cutscene dialogue data with the given id."""
        folder_path = "data/cutscenes"
        try:
            with open(folder_path + f"/{cutscene_id}.json", "r") as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            raise RuntimeError("Dialogue data file not found.")
        except OSError:
            raise RuntimeError("Cannot access dialogue data file.")
        except Exception as e:
            raise RuntimeError("An error has occured while trying to access dialogue data file.") from e