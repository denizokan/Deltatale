from tkinter import PhotoImage, messagebox
from PIL import Image, ImageTk
from pygame import mixer

class FloweyIntroCutscene:
    def __init__(self, main_game, cutscene_mgr):
        self.game = main_game
        self.cutscene_mgr = cutscene_mgr
        self.is_waiting = False
        self.cutscene_mgr.blocks_player = True
        self.flowey_interactable = self.game.current_room.interactables[0]

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
                on_complete=lambda: self.resume_timeline(self.status),
                actors={"FLOWEY": self.flowey_interactable}
            )
        
        elif self.status == "heated_up":
            self.is_waiting = True
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['heated_up'],
                on_complete=lambda: self.resume_timeline(self.status),
                actors={"FLOWEY": self.flowey_interactable}
            )

        elif self.status == "pre_battle":
            self.is_waiting = True
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['pre_battle'],
                on_complete=lambda: self.resume_timeline(self.status),
                actors={"FLOWEY": self.flowey_interactable}
            )


    def advance_phase(self, next_status):
        """Helper to transition states and wake up the update loop."""
        self.status = next_status
        self.is_waiting = False


    def resume_timeline(self, from_status):
        if from_status == "greeting":
            self.music.fadeout(1500)
            self.game.root.after(2500, lambda: self.advance_phase("heated_up"))

        elif from_status == "heated_up":
            self.play_susie_attack_animation()
            self.game.root.after(500, lambda: self.advance_phase("pre_battle"))

        elif from_status == "pre_battle": 
            print("TODO: Battle start")
            self.game.root.after(100, lambda: self.start_battle())


    # BATTLE CODE

    def start_battle(self):
        # TODO: Start scripted battle
        self.flowey_interactable["is_battling"] = True
        self.game.canvas.itemconfig(
            self.game.player.active_characters[0],
            image=self.game.player.kris_sprites["right"][0]
        )
        self.game.canvas.itemconfig(
            self.game.player.active_characters[1],
            image=self.game.player.susie_sprites["right"][0]
        )
        self.move_characters_to_battle_positions()


    def play_kris_battle_animation(self):
        self.kris_attack_sprites = [PhotoImage(file="sprites/battle/attack/kris/spr_krisb_attack_0.png").zoom(2), PhotoImage(file="sprites/battle/attack/kris/spr_krisb_attack_1.png").zoom(2), PhotoImage(file="sprites/battle/attack/kris/spr_krisb_attack_2.png").zoom(2), PhotoImage(file="sprites/battle/attack/kris/spr_krisb_attack_3.png").zoom(2), PhotoImage(file="sprites/battle/attack/kris/spr_krisb_attack_4.png").zoom(2), PhotoImage(file="sprites/battle/attack/kris/spr_krisb_attack_5.png").zoom(2), PhotoImage(file="sprites/battle/attack/kris/spr_krisb_attack_6.png").zoom(2)]

        def _play_next_frame(frame_index):
            if frame_index < len(self.kris_attack_sprites):
                self.game.canvas.itemconfig(
                    self.game.player.active_characters[0], 
                    image=self.kris_attack_sprites[frame_index]
                )
                self.game.root.after(100, lambda: _play_next_frame(frame_index + 1))
            else:
                self.play_idle_animation("kris")

        _play_next_frame(0)


    def play_susie_battle_animation(self):
        self.susie_attack_sprites = [PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_0.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_1.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_2.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_3.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_4.png").zoom(2), PhotoImage(file="sprites/battle/attack/susie/spr_susieb_attack_5.png").zoom(2)]

        def _play_next_frame(frame_index):
            if frame_index < len(self.susie_attack_sprites):
                self.game.canvas.itemconfig(
                    self.game.player.active_characters[1], 
                    image=self.susie_attack_sprites[frame_index]
                )
                self.game.root.after(100, lambda: _play_next_frame(frame_index + 1))
            else:
                self.play_idle_animation("susie")

        _play_next_frame(0)


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


    def play_idle_animation(self, char):
        if char == "kris":
            char_index = 0
            self.kris_idle_sprites = [PhotoImage(file="sprites/battle/idle/kris/spr_krisb_idle_0.png").zoom(2), PhotoImage(file="sprites/battle/idle/kris/spr_krisb_idle_1.png").zoom(2), PhotoImage(file="sprites/battle/idle/kris/spr_krisb_idle_2.png").zoom(2), PhotoImage(file="sprites/battle/idle/kris/spr_krisb_idle_3.png").zoom(2), PhotoImage(file="sprites/battle/idle/kris/spr_krisb_idle_4.png").zoom(2), PhotoImage(file="sprites/battle/idle/kris/spr_krisb_idle_5.png").zoom(2)]
            active_sprites = self.kris_idle_sprites
            
        elif char == "susie":
            char_index = 1
            self.susie_idle_sprites = [PhotoImage(file="sprites/battle/idle/susie/spr_susieb_idle_0.png").zoom(2), PhotoImage(file="sprites/battle/idle/susie/spr_susieb_idle_1.png").zoom(2), PhotoImage(file="sprites/battle/idle/susie/spr_susieb_idle_2.png").zoom(2), PhotoImage(file="sprites/battle/idle/susie/spr_susieb_idle_3.png").zoom(2)]
            active_sprites = self.susie_idle_sprites

        def _play_next_frame(frame_index):
            if frame_index > len(active_sprites) - 1:
                frame_index = 0

            self.game.canvas.itemconfig(
                self.game.player.active_characters[char_index], 
                image=active_sprites[frame_index]
            )
            self.game.root.after(100, lambda: _play_next_frame(frame_index + 1))
    
        _play_next_frame(0)


    def move_characters_to_battle_positions(self):
        kris_id = self.game.player.active_characters[0]
        susie_id = self.game.player.active_characters[1]
        flowey_id = self.game.current_room.interactables[0]["canvas_id"]

        kris_target_x, kris_target_y = 100 + 50, self.game.constants.HEIGHT // 2 - 50 
        susie_target_x, susie_target_y = 100 + 30, self.game.constants.HEIGHT // 2 + 50
        flowey_target_x, flowey_target_y = 520, self.game.constants.HEIGHT // 2 - 25

        kx, ky = self.game.canvas.coords(kris_id)[:2]
        sx, sy = self.game.canvas.coords(susie_id)[:2]
        fx, fy = self.game.canvas.coords(flowey_id)[:2]

        self.kris_ghosts = self._generate_faded_ghosts("sprites/characters/kris/walk/spr_krisr_0.png")
        self.susie_ghosts = self._generate_faded_ghosts("sprites/characters/susie/walk/spr_susier_0.png")

        total_steps = 15

        def _slide_frame(step):
            if step <= total_steps:
                t = step / total_steps

                new_kx = kx + (kris_target_x - kx) * t
                new_ky = ky + (kris_target_y - ky) * t
                new_sx = sx + (susie_target_x - sx) * t
                new_sy = sy + (susie_target_y - sy) * t
                new_fx = fx + (flowey_target_x - fx) * t
                new_fy = fy + (flowey_target_y - fy) * t

                self.game.canvas.coords(kris_id, new_kx, new_ky)
                self.game.canvas.coords(susie_id, new_sx, new_sy)
                self.game.canvas.coords(flowey_id, new_fx, new_fy)

                if step % 2 == 0: 
                    self._spawn_fading_ghost(new_kx, new_ky, self.kris_ghosts)
                    self._spawn_fading_ghost(new_sx, new_sy, self.susie_ghosts)

                self.game.root.after(16, lambda: _slide_frame(step + 1))
            else:
                mixer.Sound(file="sounds/sound_effects/snd_weaponpull.wav").play()

                # Draw swords
                self.play_susie_battle_animation()
                self.play_kris_battle_animation()
                # self.game.canvas.itemconfig(kris_id, image=self.kris_battle_idle)
          
        _slide_frame(0)


    def _generate_faded_ghosts(self, image_path, zoom=2, frames=6):
        """Pre-renders an array of fading sprites to prevent game lag."""
        original = Image.open(image_path).convert("RGBA")
        width, height = original.size
        original = original.resize((width * zoom, height * zoom), Image.NEAREST)

        ghosts = []
        for i in range(frames):
            opacity = 1.0 - (i / frames)
            r, g, b, a = original.split()
            a = a.point(lambda p: int(p * opacity))
            faded_image = Image.merge("RGBA", (r, g, b, a))

            ghosts.append(ImageTk.PhotoImage(faded_image))

        return ghosts
    

    def _spawn_fading_ghost(self, x, y, ghost_array):
        """Spawns a ghost that manages its own fade-out animation."""
        ghost_id = self.game.canvas.create_image(x, y, image=ghost_array[0], anchor="s")

        def _fade_frame(frame_index):
            if frame_index < len(ghost_array):
                self.game.canvas.itemconfig(ghost_id, image=ghost_array[frame_index])
                self.game.root.after(40, lambda: _fade_frame(frame_index + 1))
            else:
                self.game.canvas.delete(ghost_id)

        _fade_frame(0)