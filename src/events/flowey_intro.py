import math
from tkinter import PhotoImage, messagebox
from PIL import Image, ImageTk
from pygame import mixer
from src.core.enums import Action

class FloweyIntroCutscene:
    def __init__(self, main_game, cutscene_mgr):
        self.game = main_game
        self.cutscene_mgr = cutscene_mgr
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

        self.status = None
        self.music = None
        self.timeline = 0

        self.battle_started = False
        self.battle_rectangle_coords = None
        self.soul_movement = False
        self.soul_x = 0
        self.soul_y = 0

        self._preload_sprites()
        self.advance_phase(self.status)


    def update(self):
        if self.status in ["battle", "spawn_bullets", "refuse_bullets", "die"]:
            if not self.soul_movement: 
                self.handle_soul_movement()


    def advance_phase(self, from_status):
        if from_status == None: # -> Greeting
            self.update_status("greeting")
            self.flowey_music.play(-1)
            self.game.dialogue_system.start_dialogue(
                self.dialogue_data['greeting'],
                on_complete=lambda: self.advance_phase(self.status),
                actors={"FLOWEY": self.flowey_interactable}
            )

        elif from_status == "greeting": # -> Heated Up
            self.update_status("heated_up")
            self.flowey_music.fadeout(1500)
            self.game.root.after(2500, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['heated_up'],
                on_complete=lambda: self.advance_phase(self.status),
                actors={"FLOWEY": self.flowey_interactable}
            ))

        elif from_status == "heated_up": # -> Pre Battle
            self.update_status("pre_battle")
            self.play_susie_attack_animation()
            self.game.root.after(500, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['pre_battle'],
                on_complete=lambda: self.advance_phase(self.status),
                actors={"FLOWEY": self.flowey_interactable}
            ))

        elif from_status == "pre_battle": # -> Battle
            self.update_status("battle_setup")
            self.game.root.after(100, lambda: self.init_battle())

        elif from_status == "battle": # -> Spawn Bullets
            self.update_status("spawn_bullets")
            self.game.root.after(100, lambda: self.spawn_bullets())
            self.game.root.after(300, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['spawn_bullets'],
                on_complete=lambda: self.advance_phase(self.status),
                actors={"FLOWEY": self.flowey_interactable},
                is_battle=True
            ))

        elif from_status == "spawn_bullets": # -> Refuse Bullets
            self.move_bullets()

        elif from_status == "refuse_bullets": # -> Music Stop
            self.end_turn()
            self.clear_bullets()
            self.battle_mus.fadeout(1000)
            self.game.root.after(1500, lambda: self.update_status("music_stop"))
            self.game.root.after(1500, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['music_stop'],
                on_complete=lambda: self.advance_phase(self.status),
                is_battle=True
            ))

        elif from_status == "music_stop": # -> Susie Angry
            self.update_status("susie_angry")
            self.play_susie_attack_animation()
            self.game.root.after(500, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['susie_angry'],
                on_complete=lambda: self.advance_phase(self.status),
                actors={"FLOWEY": self.flowey_interactable},
                is_battle=True
            ))

        elif from_status == "susie_angry": # -> Evil Flowey
            self.update_status("evil_flowey")
            self.game.root.after(100, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['evil_flowey'],
                on_complete=lambda: self.advance_phase(self.status),
                actors={"FLOWEY": self.flowey_interactable},
                is_battle=True
            ))

        elif from_status == "evil_flowey":
            self.flowey_attack()

        elif from_status == "die": # -> Yeah Whatever
            self.close_in_bullets()

        elif from_status == "yeah_whatever": # -> Post Battle
            self.fire_rude_buster()
            self.game.root.after(1500, lambda: self.end_battle())
            self.game.root.after(1500, lambda: self.update_status("post_battle"))
            self.game.root.after(4000, lambda: self.game.dialogue_system.start_dialogue(
                self.dialogue_data['post_battle'],
                on_complete=lambda: self.advance_phase(self.status)
            ))

        elif from_status == "post_battle": # -> Cutscene End
            self.game.cutscene_manager.stop_cutscene()


    def update_status(self, next_status):
        """Helper to transition states and wake up the update loop."""
        self.status = next_status


    # BATTLE CODE

    def start_battle(self):
        self.status = "battle"
        self.battle_mus.play(-1)

        self.show_battle_ui()
        self.play_idle_animation("kris")
        self.play_idle_animation("susie")

        self.spawn_battle_rectangle()

        kris_id = self.game.player.active_characters[0]
        kx, ky = self.game.canvas.coords(kris_id)[:2]
        chest_x = kx - 30
        chest_y = ky - 50

        self.player_soul = self.game.canvas.create_image(chest_x, chest_y, image=self.player_sprite)
        self.move_soul((chest_x, chest_y), (self.game.constants.WIDTH // 2, self.game.constants.HEIGHT // 2 - 50), 15)
        self.play_chest_pulse()

        self.update_status("battle")

        self.game.dialogue_system.start_dialogue(
            self.dialogue_data['battle'],
            on_complete=lambda: self.advance_phase(self.status),
            actors={"FLOWEY": self.flowey_interactable},
            is_battle=True
        )


    def end_battle(self):
        """Fully transitions the game out of the battle state."""
        self.flowey_interactable["is_battling"] = False
        self.end_turn()
        # TODO: Hide TP bar and play battle over sprites
        self.game.root.after(1500, self.hide_battle_ui)
        self.game.root.after(1550, self.move_characters_to_original_positions)


    def end_turn(self):
        """Closes the battle UI and returns the SOUL to Kris."""
        self.update_status("ending_turn")
        self.close_battle_rectangle()
        
        kris_id = self.game.player.active_characters[0]
        kx, ky = self.game.canvas.coords(kris_id)[:2]
        chest_x = kx - 30
        chest_y = ky - 50
        self.move_soul(
            (self.soul_x, self.soul_y), 
            (chest_x, chest_y), 
            15,
            on_complete=self.returned_soul_to_body
        )


    def init_battle(self):
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


    def handle_soul_movement(self):
        target_x, target_y = self.soul_x, self.soul_y

        if self.game.input_manager.is_pressed(Action.UP):
            target_y = self.soul_y - self.game.constants.SOUL_SPEED
        if self.game.input_manager.is_pressed(Action.DOWN):
            target_y = self.soul_y + self.game.constants.SOUL_SPEED
        if self.game.input_manager.is_pressed(Action.LEFT):
            target_x = self.soul_x - self.game.constants.SOUL_SPEED
        if self.game.input_manager.is_pressed(Action.RIGHT):
            target_x = self.soul_x + self.game.constants.SOUL_SPEED

        if self.battle_rectangle_coords:
            x1, y1, x2, y2 = self.battle_rectangle_coords
        else:
            return

        soul_radius = 8
        offset = 4 

        min_x = x1 + offset + soul_radius
        max_x = x2 - offset - soul_radius
        min_y = y1 + offset + soul_radius
        max_y = y2 - offset - soul_radius

        if target_x < min_x:
            target_x = min_x
        elif target_x > max_x:
            target_x = max_x

        if target_y < min_y:
            target_y = min_y
        elif target_y > max_y:
            target_y = max_y

        if target_x != self.soul_x or target_y != self.soul_y:
            self.soul_x, self.soul_y = target_x, target_y
            self.draw_soul()


    def draw_soul(self):
        self.game.canvas.coords(self.player_soul, self.soul_x, self.soul_y)


    def spawn_bullets(self):
        """Spawns bullets behind Flowey and fans them out to the right (Up-Right to Down-Right)."""
        self.active_bullets = []
        flowey_id = self.flowey_interactable["canvas_id"]
        
        fx, fy = self.game.canvas.coords(flowey_id)[:2]
        spawn_x = fx
        spawn_y = fy
        
        num_bullets = 4
        
        for i in range(num_bullets):
            fraction = i / (num_bullets - 1) 
            
            start_angle = -(math.pi / 4) 
            total_spread = (math.pi / 2)
            angle = start_angle + (total_spread * fraction)
            
            bullet_id = self.game.canvas.create_image(spawn_x, spawn_y, image=self.flowey_bullet_sprites[0])
            self.game.canvas.tag_lower(bullet_id, flowey_id)
            
            self.active_bullets.append({
                "id": bullet_id,
                "x": spawn_x,
                "y": spawn_y,
                "angle": angle
            })

        self._animate_bullets_popping_out()
        self._animate_bullet_sprites(0)


    def _animate_bullet_sprites(self, frame_index):
        """Continuously swaps the bullet sprites to make them spin/flash."""
        if not hasattr(self, 'active_bullets') or len(self.active_bullets) == 0:
            return

        sprite_index = frame_index % 2
        
        for bullet in self.active_bullets:
            try:
                self.game.canvas.itemconfig(bullet["id"], image=self.flowey_bullet_sprites[sprite_index])
            except:
                pass

        self.game.root.after(100, lambda: self._animate_bullet_sprites(frame_index + 1))


    def _animate_bullets_popping_out(self):
        """Pushes the bullets outward from Flowey along their specific angles."""
        frames = 15
        distance_to_push = 60
        speed = distance_to_push / frames
        
        def _pop_frame(current_frame):
            if current_frame <= frames:
                for bullet in self.active_bullets:
                    bullet["x"] += math.cos(bullet["angle"]) * speed
                    bullet["y"] += math.sin(bullet["angle"]) * speed
                    
                    self.game.canvas.coords(bullet["id"], bullet["x"], bullet["y"])
                    
                self.game.root.after(30, lambda: _pop_frame(current_frame + 1))
            else:
                pass

        _pop_frame(0)


    def move_bullets(self):
        """Calculates the angle to the SOUL and moves the bullets a short distance before stopping."""
        if not hasattr(self, 'active_bullets') or len(self.active_bullets) == 0:
            return

        for bullet in self.active_bullets:
            dx = self.soul_x - bullet["x"]
            dy = self.soul_y - bullet["y"]
            bullet["target_angle"] = math.atan2(dy, dx)

        frames = 30
        speed = 3
        
        def _move_frame(current_frame):
            if current_frame <= frames:
                for bullet in self.active_bullets:
                    bullet["x"] += math.cos(bullet["target_angle"]) * speed
                    bullet["y"] += math.sin(bullet["target_angle"]) * speed
                    
                    self.game.canvas.coords(bullet["id"], bullet["x"], bullet["y"])
                
                self.game.root.after(20, lambda: _move_frame(current_frame + 1))
            else:
                self.update_status("refuse_bullets")
                self.game.dialogue_system.start_dialogue(
                    self.dialogue_data['refuse_bullets'],
                    on_complete=lambda: self.advance_phase(self.status),
                    actors={"FLOWEY": self.flowey_interactable},
                    is_battle=True
                )

        _move_frame(0)


    def clear_bullets(self, mode="backwards"):
        """
        Scatters bullets and deletes them. 
        Modes: 'backwards' (fleeing the SOUL) or 'right' (smashed by Rude Buster).
        """
        if not hasattr(self, 'active_bullets') or len(self.active_bullets) == 0:
            return

        import random

        frames = 10 if mode == "backwards" else 15

        for bullet in self.active_bullets:
            if mode == "backwards":
                speed = -15.0
                bullet["vx"] = math.cos(bullet["target_angle"]) * speed
                bullet["vy"] = math.sin(bullet["target_angle"]) * speed
            elif mode == "right":
                bullet["vx"] = random.uniform(15, 30)
                bullet["vy"] = random.uniform(-15, 15)
        
        def _scatter_frame(current_frame):
            if current_frame <= frames:
                for bullet in self.active_bullets:
                    try:
                        bullet["x"] += bullet["vx"]
                        bullet["y"] += bullet["vy"]
                        self.game.canvas.coords(bullet["id"], bullet["x"], bullet["y"])
                    except:
                        pass
                        
                self.game.root.after(20, lambda: _scatter_frame(current_frame + 1))
            else:
                for bullet in self.active_bullets:
                    try: 
                        self.game.canvas.delete(bullet["id"])
                    except: 
                        pass
                
                self.active_bullets = []

        _scatter_frame(0)


    def flowey_attack(self):
        self.spawn_battle_rectangle(width=24, height=24)

        kris_id = self.game.player.active_characters[0]
        kx, ky = self.game.canvas.coords(kris_id)[:2]
        chest_x = kx - 30
        chest_y = ky - 50
        
        self.player_soul = self.game.canvas.create_image(chest_x, chest_y, image=self.player_sprite)
        self.move_soul((chest_x, chest_y), (self.game.constants.WIDTH // 2, self.game.constants.HEIGHT // 2 - 50), 15, on_complete=self.spawn_bullets_around_soul)
        self.play_chest_pulse()


    def spawn_bullets_around_soul(self):
        """Spawns a massive ring of Friendliness Pellets around the battle box one by one."""
        self.active_bullets = []
        self.snd_pelletcreate.play()
        
        center_x = self.soul_x
        center_y = self.soul_y
        
        num_bullets = 36
        radius = 100
        
        def _spawn_single_bullet(index):
            if index < num_bullets:
                angle = (index / num_bullets) * (2 * math.pi)
                
                bx = center_x + (math.cos(angle) * radius)
                by = center_y + (math.sin(angle) * radius)
                
                bullet_id = self.game.canvas.create_image(bx, by, image=self.flowey_bullet_sprites[0])
                closing_angle = angle + math.pi 
                
                self.active_bullets.append({
                    "id": bullet_id,
                    "x": bx,
                    "y": by,
                    "angle": angle,
                    "target_angle": closing_angle
                })
                
                self.game.root.after(40, lambda: _spawn_single_bullet(index + 1))
            else:
                self.snd_pelletcreate.stop()
                self.update_status("die")
                self.game.dialogue_system.start_dialogue(
                    self.dialogue_data['die'],
                    on_complete=lambda: self.advance_phase(self.status),
                    actors={"FLOWEY": self.flowey_interactable},
                    is_battle=True
                )

        _spawn_single_bullet(0)
        self._animate_bullet_sprites(0)


    def close_in_bullets(self):
        """Animates the giant ring of bullets rapidly closing in on the SOUL and stopping before impact."""
        if not hasattr(self, 'active_bullets') or len(self.active_bullets) == 0:
            return

        self.snd_floweylaugh.play()

        frames = 70
        speed = 1
        
        def _close_in_frame(current_frame):
            if current_frame <= frames:
                for bullet in self.active_bullets:
                    try:
                        bullet["x"] += math.cos(bullet["target_angle"]) * speed
                        bullet["y"] += math.sin(bullet["target_angle"]) * speed
                        
                        self.game.canvas.coords(bullet["id"], bullet["x"], bullet["y"])
                    except:
                        pass
                
                self.game.root.after(15, lambda: _close_in_frame(current_frame + 1))
            else:
                self.snd_floweylaugh.stop()
                self.update_status("yeah_whatever")
                self.game.dialogue_system.start_dialogue(
                    self.dialogue_data['yeah_whatever'],
                    on_complete=lambda: self.advance_phase(self.status),
                    is_battle=True
                )

        _close_in_frame(0)


    def fire_rude_buster(self):
        """Fires the Rude Buster at Flowey, cycling sprites and leaving a trail of colored shadows."""
        susie_id = self.game.player.active_characters[1]
        flowey_id = self.flowey_interactable["canvas_id"]

        sx, sy = self.game.canvas.coords(susie_id)[:2]
        fx, fy = self.game.canvas.coords(flowey_id)[:2]

        spawn_x = sx + 50
        spawn_y = sy - 10

        self.play_susie_attack_animation()
        
        buster_id = self.game.canvas.create_image(spawn_x, spawn_y, image=self.rude_buster_sprites[0], anchor="center")

        total_steps = 15
        dx = (fx - spawn_x) / total_steps
        dy = (fy - spawn_y) / total_steps

        def _fly_frame(step):
            if step <= total_steps:
                self.game.canvas.move(buster_id, dx, dy)
                
                sprite_index = step % 7
                self.game.canvas.itemconfig(buster_id, image=self.rude_buster_sprites[sprite_index])
                
                if step % 2 == 0:
                    cur_x, cur_y = self.game.canvas.coords(buster_id)[:2]
                    self._spawn_fading_ghost(cur_x, cur_y, self.rude_buster_ghosts[sprite_index], anchor="center")
                    self.game.canvas.tag_raise(buster_id)
                
                if step == total_steps // 2:
                    self.clear_bullets(mode="right")
                    
                self.game.root.after(20, lambda: _fly_frame(step + 1))
            else:
                self.game.canvas.delete(buster_id)
                self.snd_floweyhit.play()
                self._knock_flowey_out()
                
        _fly_frame(0)

    def _knock_flowey_out(self):
        """Spins Flowey and launches him violently off the right side of the screen."""
        flowey_id = self.flowey_interactable["canvas_id"]
        
        frames = 30
        dx = 30
        dy = -15
        
        def _spin_frame(current_frame):
            if current_frame <= frames:
                self.game.canvas.move(flowey_id, dx, dy)
                
                spin_index = current_frame % len(self.flowey_spin_frames)
                self.game.canvas.itemconfig(flowey_id, image=self.flowey_spin_frames[spin_index])
                
                self.game.root.after(20, lambda: _spin_frame(current_frame + 1))
            else:
                self.game.canvas.itemconfig(flowey_id, state="hidden")
                
        _spin_frame(0)


    def play_battle_intro(self):
        def _play_next_frame(frame_index):
            if self.status == "battle": return

            if frame_index < len(self.kris_attack_sprites):
                self.game.canvas.itemconfig(
                    self.game.player.active_characters[0], 
                    image=self.kris_attack_sprites[frame_index]
                )

            if frame_index < len(self.susie_attack_sprites):
                self.game.canvas.itemconfig(
                    self.game.player.active_characters[1], 
                    image=self.susie_attack_sprites[frame_index]
                )

            if frame_index > 4:
                self.start_battle()
            self.game.root.after(100, lambda: _play_next_frame(frame_index + 1))

        _play_next_frame(0)


    def play_susie_attack_animation(self):
        self.snd_laz.play()

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
            active_sprites = self.kris_idle_sprites
            
        elif char == "susie":
            char_index = 1
            active_sprites = self.susie_idle_sprites

        def _play_next_frame(frame_index):
            if self.status == "post_battle": return
            if char_index == 1 and (self.status == "susie_angry" or self.status == "yeah_whatever"):
                self.game.root.after(100, lambda: _play_next_frame(frame_index))
                return

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
        flowey_id = self.flowey_interactable["canvas_id"]

        self.original_character_positions = [(self.game.canvas.coords(kris_id)[:2], self.game.player.facing), (self.game.canvas.coords(susie_id)[:2], self.game.player.history[0][2])]

        kris_target_x, kris_target_y = 100 + 50, self.game.constants.HEIGHT // 2 - 50 
        susie_target_x, susie_target_y = 100 + 30, self.game.constants.HEIGHT // 2 + 50
        flowey_target_x, flowey_target_y = 520, self.game.constants.HEIGHT // 2 - 25

        kx, ky = self.game.canvas.coords(kris_id)[:2]
        sx, sy = self.game.canvas.coords(susie_id)[:2]
        fx, fy = self.game.canvas.coords(flowey_id)[:2]

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
                self.snd_weapon.play()

                # Draw swords
                self.play_battle_intro()
          
        _slide_frame(0)


    def move_characters_to_original_positions(self):
        """Slides Kris and Susie back to their saved overworld positions and resets their sprites."""
        kris_id = self.game.player.active_characters[0]
        susie_id = self.game.player.active_characters[1]

        kris_saved_coords, kris_facing = self.original_character_positions[0]
        susie_saved_coords, susie_facing = self.original_character_positions[1]

        self.game.canvas.itemconfig(kris_id, image=self.game.player.kris_sprites[kris_facing][0])
        self.game.canvas.itemconfig(susie_id, image=self.game.player.susie_sprites[susie_facing][0])

        kris_target_x, kris_target_y = kris_saved_coords
        susie_target_x, susie_target_y = susie_saved_coords

        kx, ky = self.game.canvas.coords(kris_id)[:2]
        sx, sy = self.game.canvas.coords(susie_id)[:2]

        total_steps = 30

        def _slide_frame(step):
            if step <= total_steps:
                t = step / total_steps
                ease_t = 1 - (1 - t)**3

                new_kx = kx + (kris_target_x - kx) * ease_t
                new_ky = ky + (kris_target_y - ky) * ease_t
                new_sx = sx + (susie_target_x - sx) * ease_t
                new_sy = sy + (susie_target_y - sy) * ease_t

                self.game.canvas.coords(kris_id, new_kx, new_ky)
                self.game.canvas.coords(susie_id, new_sx, new_sy)

                self.game.root.after(16, lambda: _slide_frame(step + 1))
            else:
                pass
          
        _slide_frame(0)


    def show_battle_ui(self):
        lower_ui_start_y = self.game.constants.HEIGHT + 150
        lower_ui_target_y = self.game.constants.HEIGHT
        lower_ui_x = self.game.constants.WIDTH // 2

        tp_ui_start_x = -100
        tp_ui_target_x = 10
        tp_ui_y = 50

        self.lower_ui_id = self.game.canvas.create_image(
            lower_ui_x, lower_ui_start_y, 
            image=self.battle_lower_ui, anchor="s"
        )
        self.tp_ui_id = self.game.canvas.create_image(
            tp_ui_start_x, tp_ui_y, 
            image=self.battle_tp_ui, anchor="nw"
        )

        total_frames = 20

        def _animate_ui(frame):
            if frame <= total_frames:
                t = frame / total_frames

                ease_t = 1 - (1 - t)**3

                current_lower_y = lower_ui_start_y + (lower_ui_target_y - lower_ui_start_y) * ease_t
                current_tp_x = tp_ui_start_x + (tp_ui_target_x - tp_ui_start_x) * ease_t

                self.game.canvas.coords(self.lower_ui_id, lower_ui_x, current_lower_y)
                self.game.canvas.coords(self.tp_ui_id, current_tp_x, tp_ui_y)

                self.game.root.after(16, lambda: _animate_ui(frame + 1))
            else:
                self.game.canvas.coords(self.lower_ui_id, lower_ui_x, lower_ui_target_y)
                self.game.canvas.coords(self.tp_ui_id, tp_ui_target_x, tp_ui_y)

        _animate_ui(0)


    def hide_battle_ui(self):
        """Slides the Battle UI off-screen and deletes it."""
        lower_ui_start_y = self.game.constants.HEIGHT
        lower_ui_target_y = self.game.constants.HEIGHT + 150
        lower_ui_x = self.game.constants.WIDTH // 2

        tp_ui_start_x = 10
        tp_ui_target_x = -100
        tp_ui_y = 50

        total_frames = 20

        def _animate_ui_out(frame):
            if frame <= total_frames:
                t = frame / total_frames
                ease_t = t**3

                current_lower_y = lower_ui_start_y + (lower_ui_target_y - lower_ui_start_y) * ease_t
                current_tp_x = tp_ui_start_x + (tp_ui_target_x - tp_ui_start_x) * ease_t

                try:
                    self.game.canvas.coords(self.lower_ui_id, lower_ui_x, current_lower_y)
                    self.game.canvas.coords(self.tp_ui_id, current_tp_x, tp_ui_y)
                except: 
                    pass

                self.game.root.after(16, lambda: _animate_ui_out(frame + 1))
            else:
                try:
                    self.game.canvas.delete(self.lower_ui_id)
                    self.game.canvas.delete(self.tp_ui_id)
                except: 
                    pass

        _animate_ui_out(0)


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
    

    def _spawn_fading_ghost(self, x, y, ghost_array, anchor="s"):
        """Spawns a ghost that manages its own fade-out animation."""
        ghost_id = self.game.canvas.create_image(x, y, image=ghost_array[0], anchor=anchor)

        def _fade_frame(frame_index):
            if frame_index < len(ghost_array):
                self.game.canvas.itemconfig(ghost_id, image=ghost_array[frame_index])
                self.game.root.after(40, lambda: _fade_frame(frame_index + 1))
            else:
                self.game.canvas.delete(ghost_id)

        _fade_frame(0)


    def move_soul(self, start_coords, end_coords, frames, on_complete=None):
        """Moves the player soul to the given coordinates over x frames."""
        start_x, start_y = start_coords
        end_x, end_y = end_coords
        self.soul_movement = True

        def _animate_soul(frame_index):
            if frame_index <= frames:
                t = frame_index / frames
                
                ease_t = 1 - (1 - t)**3
                
                cur_x = start_x + (end_x - start_x) * ease_t
                cur_y = start_y + (end_y - start_y) * ease_t
                
                self.game.canvas.coords(self.player_soul, cur_x, cur_y)
                self.soul_x, self.soul_y = cur_x, cur_y
                self.game.root.after(int(1000 / self.game.constants.FPS), lambda: _animate_soul(frame_index + 1))
            else:
                self.soul_movement = False
                self.game.canvas.coords(self.player_soul, end_x, end_y)
                self.soul_x, self.soul_y = end_x, end_y
                
                if on_complete:
                    on_complete()

        _animate_soul(0)


    def spawn_battle_rectangle(self, width=160, height=160):
        """Spawns the battle box using a solid expanding void and hollow fading trails."""
        if self.battle_rectangle_coords != None: raise RuntimeError("Can't spawn a new battle rectangle because another one is already present.")
        target_width = width
        target_height = height
        box_x, box_y = self.game.constants.WIDTH // 2, self.game.constants.HEIGHT // 2 - 50

        self.battle_rectangle_coords = (box_x - target_width/2, box_y - target_height/2, box_x + target_width/2, box_y + target_height/2)
        total_frames = 20

        self.main_anim_poly = self.game.canvas.create_polygon(
            0, 0, 0, 0, 0, 0, 0, 0,
            outline="#00ff00",
            fill="black",
            width=4
        )
        self.game.canvas.tag_lower(self.main_anim_poly, self.game.player.active_characters[0])

        def _get_rotated_corners(cx, cy, w, h, angle):
            """Calculates the 4 corners of a rotated rectangle."""
            hw, hh = w / 2, h / 2
            corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
            rotated_coords = []
            
            for x_off, y_off in corners:
                rx = x_off * math.cos(angle) - y_off * math.sin(angle)
                ry = x_off * math.sin(angle) + y_off * math.cos(angle)
                rotated_coords.extend([cx + rx, cy + ry])
                
            return rotated_coords

        def _spawn_fading_ghost(coords):
            """Spawns a hollow polygon that fades itself out."""
            poly_id = self.game.canvas.create_polygon(
                *coords,
                outline="#00ff00",
                fill="",
                width=4
            )
            self.game.canvas.tag_raise(poly_id, self.main_anim_poly)
            
            fade_colors = ["#00cc00", "#009900", "#006600", "#003300", "delete"]
            def _fade_step(step_index):
                if step_index < len(fade_colors):
                    color = fade_colors[step_index]
                    if color == "delete":
                        self.game.canvas.delete(poly_id)
                    else:
                        self.game.canvas.itemconfig(poly_id, outline=color)
                        self.game.root.after(70, lambda: _fade_step(step_index + 1))
                        
            self.game.root.after(70, lambda: _fade_step(0))

        def _play_anim_frame(frame_index):
            if frame_index <= total_frames:
                t = frame_index / total_frames
                ease_t = 1 - (1 - t)**3

                self.game.canvas.itemconfig(
                    self.game.current_room.background, 
                    image=self._dark_bg_frames[frame_index]
                )
                
                current_w = target_width * ease_t
                current_h = target_height * ease_t
                current_angle = math.pi * (1 - ease_t)

                coords = _get_rotated_corners(box_x, box_y, current_w, current_h, current_angle)
                
                self.game.canvas.coords(self.main_anim_poly, *coords)
                
                if t < 0.35:
                    _spawn_fading_ghost(coords)

                self.game.root.after(25, lambda: _play_anim_frame(frame_index + 1))
            else:
                self.game.canvas.delete(self.main_anim_poly)
    
                self.battle_box_id = self.game.canvas.create_rectangle(
                    box_x - target_width/2, box_y - target_height/2,
                    box_x + target_width/2, box_y + target_height/2,
                    outline="#00ff00",
                    fill="black",
                    width=4
                )
                
                self.game.canvas.tag_lower(self.battle_box_id, self.game.player.active_characters[0])

        _play_anim_frame(0)


    def close_battle_rectangle(self):
        """Closes the battle box using a reverse spinning animation and fades out the darkness."""
        if self.battle_rectangle_coords == None: raise RuntimeError("There is no battle rectangle to close.")
        x1, y1, x2, y2 = self.battle_rectangle_coords
        self.battle_rectangle_coords = None
        target_width = x2 - x1
        target_height = y2 - y1
        box_x, box_y = self.game.constants.WIDTH // 2, self.game.constants.HEIGHT // 2 - 50
        total_frames = 20

        if hasattr(self, 'battle_box_id'):
            self.game.canvas.delete(self.battle_box_id)

        self.main_anim_poly = self.game.canvas.create_polygon(
            0, 0, 0, 0, 0, 0, 0, 0,
            outline="#00ff00",
            fill="black",
            width=4
        )
        self.game.canvas.tag_lower(self.main_anim_poly, self.game.player.active_characters[0])

        def _get_rotated_corners(cx, cy, w, h, angle):
            """Calculates the 4 corners of a rotated rectangle."""
            hw, hh = w / 2, h / 2
            corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
            rotated_coords = []
            
            for x_off, y_off in corners:
                rx = x_off * math.cos(angle) - y_off * math.sin(angle)
                ry = x_off * math.sin(angle) + y_off * math.cos(angle)
                rotated_coords.extend([cx + rx, cy + ry])
                
            return rotated_coords

        def _spawn_fading_ghost(coords):
            """Spawns a hollow polygon that fades itself out."""
            poly_id = self.game.canvas.create_polygon(
                *coords,
                outline="#00ff00",
                fill="",
                width=4
            )
            self.game.canvas.tag_raise(poly_id, self.main_anim_poly)
            
            fade_colors = ["#00cc00", "#009900", "#006600", "#003300", "delete"]
            def _fade_step(step_index):
                if step_index < len(fade_colors):
                    color = fade_colors[step_index]
                    if color == "delete":
                        self.game.canvas.delete(poly_id)
                    else:
                        self.game.canvas.itemconfig(poly_id, outline=color)
                        self.game.root.after(30, lambda: _fade_step(step_index + 1))
                        
            self.game.root.after(30, lambda: _fade_step(0))

        def _play_anim_frame(frame_index):
            if frame_index <= total_frames:
                t = frame_index / total_frames
                ease_t = (1 - t)**3

                self.game.canvas.itemconfig(
                    self.game.current_room.background, 
                    image=self._light_bg_frames[frame_index]
                )
                
                current_w = target_width * ease_t
                current_h = target_height * ease_t
                
                current_angle = math.pi * (1 - ease_t)

                coords = _get_rotated_corners(box_x, box_y, current_w, current_h, current_angle)
                self.game.canvas.coords(self.main_anim_poly, *coords)
                
                if ease_t < 0.35:
                    _spawn_fading_ghost(coords)

                self.game.root.after(25, lambda: _play_anim_frame(frame_index + 1))
            else:
                self.game.canvas.delete(self.main_anim_poly)
                self.game.canvas.itemconfig(
                    self.game.current_room.background, 
                    image=self.game.current_room.bg_image 
                )

        _play_anim_frame(0)


    def play_chest_pulse(self):
        """Spawns the pulse on Kris's chest."""
        kris_id = self.game.player.active_characters[0]
        kx, ky = self.game.canvas.coords(kris_id)[:2]
        chest_x = kx - 30
        chest_y = ky - 50
        
        pulse_id = self.game.canvas.create_image(
            chest_x, chest_y, 
            image=self.pulse_frames[0], 
            anchor="center"
        )
        
        def _play_pulse_frame(frame_index):
            if frame_index >= len(self.pulse_frames):
                self.game.canvas.delete(pulse_id)
                return
                
            self.game.canvas.itemconfig(pulse_id, image=self.pulse_frames[frame_index])
            self.game.root.after(40, lambda: _play_pulse_frame(frame_index + 1))
            
        _play_pulse_frame(0)


    def _generate_pulse_frames(self, image_path, base_zoom=2, max_zoom=5, frames=15):
        """Pre-renders an expanding, fading pulse effect for the SOUL."""
        original = Image.open(image_path).convert("RGBA")
        base_w, base_h = original.size
        
        pulse_frames = []
        for i in range(frames):
            t = i / (frames - 1)
            
            current_zoom = base_zoom + ((max_zoom - base_zoom) * t)
            opacity = 1.0 - t
            
            new_w = int(base_w * current_zoom)
            new_h = int(base_h * current_zoom)
            resized = original.resize((new_w, new_h), Image.NEAREST)
            
            r, g, b, a = resized.split()
            a = a.point(lambda p: int(p * opacity))
            faded_image = Image.merge("RGBA", (r, g, b, a))
            
            pulse_frames.append(ImageTk.PhotoImage(faded_image))
            
        return pulse_frames


    def _generate_rotated_frames(self, image_path, zoom=2, frames=8):
        """Pre-renders an array of rotated sprites to prevent lag during the hit animation."""
        original = Image.open(image_path).convert("RGBA")
        width, height = original.size
        original = original.resize((width * zoom, height * zoom), Image.NEAREST)

        rotated_frames = []
        for i in range(frames):
            angle = i * (360 / frames)
            rotated_image = original.rotate(angle, expand=True) 
            rotated_frames.append(ImageTk.PhotoImage(rotated_image))

        return rotated_frames


    def fade_out_soul(self):
        """Fades out the player SOUL and removes it from the canvas."""
        def _play_fade(frame_index):
            if frame_index < len(self.soul_fade_frames):
                self.game.canvas.itemconfig(self.player_soul, image=self.soul_fade_frames[frame_index])
                self.game.root.after(30, lambda: _play_fade(frame_index + 1))
            else:
                self.game.canvas.delete(self.player_soul)
                
        _play_fade(0)


    def returned_soul_to_body(self):
        self.fade_out_soul()
        self.play_chest_pulse()


    def _preload_sprites(self):
        """Loads and caches all dynamic sprites into memory once during initialization."""
        self.kris_attack_sprites = [
            PhotoImage(file=f"sprites/battle/attack/kris/spr_krisb_attack_{i}.png").zoom(2)
            for i in range(7)
        ]
        self.susie_attack_sprites = [
            PhotoImage(file=f"sprites/battle/attack/susie/spr_susieb_attack_{i}.png").zoom(2)
            for i in range(6)
        ]
        self.kris_idle_sprites = [
            PhotoImage(file=f"sprites/battle/idle/kris/spr_krisb_idle_{i}.png").zoom(2)
            for i in range(6)
        ]
        self.susie_idle_sprites = [
            PhotoImage(file=f"sprites/battle/idle/susie/spr_susieb_idle_{i}.png").zoom(2)
            for i in range(4)
        ]

        self.flowey_bullet_sprites = [
            PhotoImage(file=f"sprites/characters/flowey/bullets/spr_pellet_{i}.png")
            for i in range(2)
        ]

        self.rude_buster_sprites = [
            PhotoImage(file=f"sprites/battle/attack/susie/spr_rudebuster_beam_{i}.png").zoom(2)
            for i in range(7)
        ]

        self.player_sprite = PhotoImage(file="sprites/SOUL.png")

        # Ghost references
        self.kris_ghosts = self._generate_faded_ghosts("sprites/characters/kris/walk/spr_krisr_0.png")
        self.susie_ghosts = self._generate_faded_ghosts("sprites/characters/susie/walk/spr_susier_0.png")
        self.pulse_frames = self._generate_pulse_frames("sprites/SOUL.png", base_zoom=2, max_zoom=4.5, frames=12)
        self.soul_fade_frames = self._generate_faded_ghosts("sprites/SOUL.png", zoom=1, frames=10)
        self.rude_buster_ghosts = [
            self._generate_faded_ghosts(f"sprites/battle/attack/susie/spr_rudebuster_beam_{i}.png", zoom=2, frames=5)
            for i in range(7)
        ]
        self.flowey_spin_frames = self._generate_rotated_frames("sprites/characters/flowey/pngs/spr_flowey_0.png", zoom=2, frames=8)

        # Sound effects & musics
        self.snd_laz = mixer.Sound(file="sounds/sound_effects/snd_laz_c.wav")
        self.snd_weapon = mixer.Sound(file="sounds/sound_effects/snd_weaponpull.wav")
        self.snd_pelletcreate = mixer.Sound(file="sounds/sound_effects/snd_floweypelletscreate.mp3")
        self.snd_floweylaugh = mixer.Sound(file="sounds/sound_effects/snd_floweylaugh.wav")
        self.snd_floweyhit = mixer.Sound(file="sounds/sound_effects/snd_floweyhurt.wav")
        self.flowey_music = mixer.Sound("sounds/mus_flowey.ogg")
        self.battle_mus = mixer.Sound(file="sounds/battle.ogg")

        # Battle UI
        self.battle_lower_ui = PhotoImage(file="sprites/battle/ui/flowey_fight_lower_ui.png")
        self.battle_tp_ui = PhotoImage(file="sprites/battle/ui/flowey_fight_tp_bar.png")

        # Battle box
        self._dark_bg_frames = []
        self._light_bg_frames = []
        total_frames = 20
        max_darkness = 200

        bg_path = self.game.current_room.room_data["bg_image"]
        pil_img = Image.open(bg_path).convert("RGBA")
        w, h = pil_img.size
        original_bg = pil_img.resize((w * 2, h * 2), Image.NEAREST)

        for i in range(total_frames + 1):
            t = i / total_frames

            ease_t_dark = 1 - (1 - t)**3
            alpha_dark = int(max_darkness * ease_t_dark)
            dark_layer = Image.new("RGBA", original_bg.size, (0, 0, 0, alpha_dark))
            baked_dark = Image.alpha_composite(original_bg, dark_layer)
            self._dark_bg_frames.append(ImageTk.PhotoImage(baked_dark))

            ease_t_light = (1 - t)**3
            alpha_light = int(max_darkness * ease_t_light)
            light_layer = Image.new("RGBA", original_bg.size, (0, 0, 0, alpha_light))
            baked_light = Image.alpha_composite(original_bg, light_layer)
            self._light_bg_frames.append(ImageTk.PhotoImage(baked_light))