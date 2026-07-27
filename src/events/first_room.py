from tkinter import messagebox, PhotoImage
from pygame import mixer

class FirstRoomCutscene:
    def __init__(self, main_game, cutscene_mgr):
        self.game = main_game
        self.cutscene_mgr = cutscene_mgr
        self.is_waiting = False
        self.cutscene_mgr.blocks_player = True
    
        try:
            self.dialogue_data = self.cutscene_mgr.load_json("first_room")
        except RuntimeError as e:
            self.game.root.destroy()
            messagebox.showerror(
                "An error has occured.",
                f"{e}"
            )
            exit(1)

        self.kris_spawn_x = 270
        self.kris_spawn_y = 220
        self.susie_spawn_x = 330
        self.susie_spawn_y = 220

        self.kris_sprites = [PhotoImage(file="sprites/characters/kris/spr_krisd_0.png").zoom(2), PhotoImage(file="sprites/characters/kris/spr_krisr_0.png").zoom(2)]
        self.susie_sprites = [PhotoImage(file="sprites/characters/susie/walk/spr_susied_0.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susiel_0.png").zoom(2)]

        self.game.player.x, self.game.player.y = self.kris_spawn_x,self.kris_spawn_y
        self.game.canvas.coords(self.game.player.active_characters[0], self.kris_spawn_x - self.game.camera.x, self.kris_spawn_y - self.game.camera.y)
        self.game.canvas.itemconfig(self.game.player.active_characters[0], image=self.kris_sprites[0])
        self.game.canvas.coords(self.game.player.active_characters[1], self.susie_spawn_x - self.game.camera.x, self.susie_spawn_y - self.game.camera.y)
    
        self.status = "pilot"
        self.timeline = 0
    
    
    def update(self):
        if self.is_waiting: return
    
        if self.status == "pilot":
            self.is_waiting = True
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['pilot'],
                on_complete=lambda: self.resume_timeline(self.status)
            )
    
        elif self.status == "waking_up":
            self.is_waiting = True
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['waking_up'],
                on_complete=lambda: self.resume_timeline(self.status)
            )
    
        elif self.status == "axe_realization":
            self.is_waiting = True
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['axe_realization'],
                on_complete=lambda: self.resume_timeline(self.status)
            )

        elif self.status == "after_realization":
            self.is_waiting = True
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['after_realization'],
                on_complete=lambda: self.resume_timeline(self.status)
            )
    
    
    def advance_phase(self, next_status):
        """Helper to transition states and wake up the update loop."""
        self.status = next_status
        self.is_waiting = False
    
    
    def resume_timeline(self, from_status):
        if from_status == "pilot":
            self.game.transition.fade_from_black(speed=12)
            self.game.root.after(2500, lambda: self.advance_phase("waking_up"))
    
        elif from_status == "waking_up":
            self.game.canvas.itemconfig(self.game.player.active_characters[0], image=self.kris_sprites[1])
            self.play_susie_attack_animation()
            self.game.root.after(500, lambda: self.advance_phase("axe_realization"))

        elif from_status == "axe_realization":
            self.game.canvas.itemconfig(
                self.game.player.active_characters[1], 
                image=self.susie_sprites[1]
            )

            self.game.root.after(100, lambda: self.advance_phase("after_realization"))
    
        elif from_status == "after_realization":
            self.game.canvas.coords(self.game.player.active_characters[1], self.kris_spawn_x, self.kris_spawn_y + 20)
            self.game.canvas.itemconfig(
                self.game.player.active_characters[1], 
                image=self.susie_sprites[0]
            )
            self.game.root.after(100, lambda: self.game.cutscene_manager.stop_cutscene())


    def play_susie_attack_animation(self):
        self.susie_attack_sprites = [PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_0.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_1.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_2.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_3.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_4.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_5.png").zoom(2)]

        mixer.Sound(file="sounds/sound_effects/snd_laz_c.wav").play()

        def _play_next_frame(frame_index):
            if frame_index < len(self.susie_attack_sprites):
                self.game.canvas.itemconfig(
                    self.game.player.active_characters[1], 
                    image=self.susie_attack_sprites[frame_index]
                )
                self.game.root.after(100, lambda: _play_next_frame(frame_index + 1))

        _play_next_frame(0)