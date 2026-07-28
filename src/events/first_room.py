from tkinter import messagebox, PhotoImage
from pygame import mixer

class FirstRoomCutscene:
    def __init__(self, main_game, cutscene_mgr):
        self.game = main_game
        self.cutscene_mgr = cutscene_mgr
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

        self.kris_sprites = [PhotoImage(file="sprites/characters/kris/spr_dkris_ground_0.png").zoom(2), PhotoImage(file="sprites/characters/kris/spr_dkris_ground_1.png").zoom(2), PhotoImage(file="sprites/characters/kris/spr_dkris_ground_2.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisd_0.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisr_0.png").zoom(2)]
        self.susie_sprites = [PhotoImage(file="sprites/characters/susie/walk/spr_susied_0.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susiel_0.png").zoom(2)]

        self.game.player.x, self.game.player.y = self.kris_spawn_x,self.kris_spawn_y
        self.game.canvas.coords(self.game.player.active_characters[0], self.kris_spawn_x - self.game.camera.x, self.kris_spawn_y - self.game.camera.y)
        self.game.canvas.itemconfig(self.game.player.active_characters[0], image=self.kris_sprites[0])
        self.game.canvas.coords(self.game.player.active_characters[1], self.susie_spawn_x - self.game.camera.x, self.susie_spawn_y - self.game.camera.y)
        self.game.canvas.itemconfig(self.game.player.active_characters[1], image=self.susie_sprites[1])
    
        self.status = None
        self.timeline = 0

        self.advance_phase(self.status)
    
    
    def update(self):
        pass
    
    
    def advance_phase(self, from_status):
        if from_status == None: # -> Pilot
            self.update_status("pilot")
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['pilot'],
                on_complete=lambda: self.advance_phase(self.status)
            )

        elif from_status == "pilot": # -> Waking Up
            self.update_status("waking_up")
            self.game.transition.fade_from_black(speed=12)
            self.game.root.after(2000, lambda: self.play_kris_get_up())
            self.game.root.after(4000, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['waking_up'],
                on_complete=lambda: self.advance_phase(self.status)
            ))
    
        elif from_status == "waking_up": # -> Axe Realization
            self.update_status("axe_realization")
            self.play_susie_attack_animation()
            self.game.root.after(500, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['axe_realization'],
                on_complete=lambda: self.advance_phase(self.status)
            ))

        elif from_status == "axe_realization": # -> After Realization
            self.update_status("after_realization")
            self.game.canvas.itemconfig(
                self.game.player.active_characters[1], 
                image=self.susie_sprites[1]
            )

            self.game.root.after(100, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['after_realization'],
                on_complete=lambda: self.advance_phase(self.status)
            ))
    
        elif from_status == "after_realization": # -> Cutscene End
            self.game.canvas.itemconfig(
                self.game.player.active_characters[0], 
                image=self.kris_sprites[3]
            )
            self.game.player._move_susie_behind_kris(susie_start_coords=(self.susie_spawn_x, self.susie_spawn_y), kris_facing="down")
            self.game.root.after(1000, lambda: self.game.cutscene_manager.stop_cutscene())


    def update_status(self, next_status):
        """Helper to transition states and wake up the update loop."""
        self.status = next_status


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


    def play_kris_get_up(self):
        def _play_next_frame(frame_index):
            if frame_index < len(self.kris_sprites) - 2:
                self.game.canvas.itemconfig(
                    self.game.player.active_characters[0], 
                    image=self.kris_sprites[frame_index]
                )
                self.game.root.after(400, lambda: _play_next_frame(frame_index + 1))

            else:
                if frame_index > 4: return
                self.game.canvas.itemconfig(
                    self.game.player.active_characters[0], 
                    image=self.kris_sprites[frame_index]
                )
                self.game.root.after(500, lambda: _play_next_frame(frame_index + 1))
            
        _play_next_frame(0)