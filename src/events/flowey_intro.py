from tkinter import messagebox
from pygame import mixer

class FloweyIntroCutscene:
    def __init__(self, main_game, cutscene_mgr):
        self.game = main_game
        self.cutscene_mgr = cutscene_mgr
        self.is_waiting = False
        self.cutscene_mgr.blocks_player = True

        try:
            self.dialogue_data = self.cutscene_mgr.load_json("flowey_first_interaction")
        except RuntimeError as e:
            self.game.root.destroy()
            messagebox.showerror(
                "An error has occured.",
                f"{e}"
            )
            exit(1)

        self.status = "greeting"
        self.music = None
        self.timeline = 0


    def update(self):
        if self.is_waiting: return

        if self.status == "greeting":
            self.is_waiting = True
            self.music = mixer.Sound("sounds/mus_flowey.ogg")
            self.music.play(-1)
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['greeting'],
                on_complete=lambda: self.resume_timeline(self.status)
            )
        
        elif self.status == "heated_up":
            self.is_waiting = True
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['heated_up'],
                on_complete=lambda: self.resume_timeline(self.status)
            )

        elif self.status == "pre_battle":
            self.is_waiting = True
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['pre_battle'],
                on_complete=lambda: self.resume_timeline(self.status)
            )


    def start_battle(self):
        # TODO: Start scripted battle
        pass


    def advance_phase(self, next_status):
        """Helper to transition states and wake up the update loop."""
        self.status = next_status
        self.is_waiting = False


    def resume_timeline(self, from_status):
        if from_status == "greeting": 
            self.music.fadeout(1500)
            self.game.root.after(3000, lambda: self.advance_phase("heated_up"))

        elif from_status == "heated_up": 
            print("TODO: Susie axe effect")
            self.game.root.after(1000, lambda: self.advance_phase("pre_battle"))

        elif from_status == "pre_battle": 
            print("TODO: Battle start")
            self.game.root.after(100, lambda: self.start_battle())