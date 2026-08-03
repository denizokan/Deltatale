import pygame
import math
from src.core.enums import Action
from src.core.constants import Constants

class Ghost:
    """Helper class to manage fading trailing sprites."""
    def __init__(self, image, x, y, start_alpha=150, decay=10):
        self.image = image.copy()
        self.x = x
        self.y = y
        self.alpha = start_alpha
        self.decay = decay

    def update(self):
        self.alpha -= self.decay
        return self.alpha > 0

    def draw(self, surface):
        self.image.set_alpha(self.alpha)
        # Drawn purely in screen space now!
        surface.blit(self.image, (self.x, self.y))


class FloweyIntroCutscene:
    def __init__(self, context, cutscene_mgr):
        self.context = context
        self.cutscene_mgr = cutscene_mgr
        self.cutscene_mgr.blocks_player = True
        
        self.player = self.context.world.player
        self.flowey_interactable = self.context.world.current_room.interactables[0]

        try:
            self.dialogue_data = self.cutscene_mgr.load_json("flowey_first_interaction")
        except RuntimeError as e:
            print(f"An error has occurred: {e}")
            pygame.quit()
            exit(1)

        # State Machine
        self.status = "pilot"
        self.state_timer = pygame.time.get_ticks()
        
        # Independent Continuous Animation Timers
        self.kris_anim_state = "overworld" # "overworld", "battle_idle", "attack", "attack_hold"
        self.kris_anim_frame = 0
        self.kris_anim_timer = pygame.time.get_ticks()
        
        self.susie_anim_state = "overworld"
        self.susie_anim_frame = 0
        self.susie_anim_timer = pygame.time.get_ticks()
        
        # Screen-Space Coordinates (Decoupled from world/camera!)
        self.kris_screen_x, self.kris_screen_y = 0, 0
        self.susie_screen_x, self.susie_screen_y = 0, 0
        self.flowey_screen_x, self.flowey_screen_y = 0, 0
        
        # Battle & Animation Variables
        self.battle_started = False
        self.darkness_alpha = 0
        self.battle_box = None 
        self.box_angle = 0
        
        self.soul_x, self.soul_y = 0, 0
        self.soul_movement = False
        self.pulse_timer = 0
        
        self.bullets = []
        self.ghosts = []
        
        self.ui_y_offset = 150
        self.tp_x_offset = -150
        
        self.flowey_override_sprite = None
        self.flowey_angle = 0
        self.rude_buster = None

        self._preload_sprites()
        
        # Hide the real Player objects entirely during this cutscene
        # We will manually draw them in screen-space in our draw() method!
        empty_surf = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.player.cutscene_sprite_override = empty_surf
        self.player.cutscene_sprite_override_susie = empty_surf
        
        # Lock in their starting screen-coordinates based on the current camera
        cam = self.context.world.camera
        self.kris_screen_x = self.player.x - cam.x
        self.kris_screen_y = self.player.y - cam.y
        self.susie_screen_x = self.player.history[0][0] - cam.x
        self.susie_screen_y = self.player.history[0][1] - cam.y
        
        self.context.dialogue.start_dialogue(
            self.dialogue_data['greeting'],
            on_complete=self.on_greeting_done,
            actors={"FLOWEY": self.flowey_interactable}
        )
        self.flowey_music.play(-1)


    # ==========================================
    # CALLBACKS (Triggers when dialogue boxes close)
    # ==========================================

    def on_greeting_done(self):
        self.status = "heated_up_delay"
        self.state_timer = pygame.time.get_ticks()
        self.flowey_music.fadeout(1500)

    def on_heated_up_done(self):
        self.status = "pre_battle"
        self.state_timer = pygame.time.get_ticks()
        
        # Trigger Susie's continuous attack animation!
        self.susie_anim_state = "attack"
        self.susie_anim_frame = 0
        self.snd_laz.play()

    def on_pre_battle_done(self):
        self.status = "battle_setup"
        self.state_timer = pygame.time.get_ticks()
        
        # Return them to overworld pose for the slide
        self.susie_anim_state = "overworld"
        self.susie_anim_frame = 0
        
        # Save exact coordinates for the slide math
        self.original_kris_sx, self.original_kris_sy = self.kris_screen_x, self.kris_screen_y
        self.original_susie_sx, self.original_susie_sy = self.susie_screen_x, self.susie_screen_y
        
        cam = self.context.world.camera
        self.original_flowey_sx = self.flowey_interactable["x"] - cam.x
        self.original_flowey_sy = self.flowey_interactable["y"] - cam.y
        self.flowey_screen_x, self.flowey_screen_y = self.original_flowey_sx, self.original_flowey_sy

    def on_battle_intro_done(self):
        self.status = "spawn_bullets"
        self.state_timer = pygame.time.get_ticks()
        self._init_bullet_spread()

    def on_spawn_bullets_done(self):
        self.status = "move_bullets"
        self.state_timer = pygame.time.get_ticks()

    def on_refuse_bullets_done(self):
        self.status = "music_stop"
        self.state_timer = pygame.time.get_ticks()
        self.battle_mus.fadeout(1000)
        self.clear_bullets(mode="backwards")
        self.soul_movement = False
        self.original_soul_x, self.original_soul_y = self.soul_x, self.soul_y

    def on_music_stop_done(self):
        self.status = "susie_angry"
        self.state_timer = pygame.time.get_ticks()
        
        # Trigger Susie attack, but Kris stays in "battle_idle" so he keeps bouncing!
        self.susie_anim_state = "attack"
        self.susie_anim_frame = 0
        self.snd_laz.play()

    def on_susie_angry_done(self):
        self.status = "evil_flowey"
        self.state_timer = pygame.time.get_ticks()

    def on_evil_flowey_done(self):
        self.status = "flowey_attack_setup"
        self.state_timer = pygame.time.get_ticks()
        
        chest_x = self.kris_screen_x - 30
        chest_y = self.kris_screen_y - 50
        self.soul_x, self.soul_y = chest_x, chest_y
        self.original_soul_x, self.original_soul_y = chest_x, chest_y
        self.pulse_timer = pygame.time.get_ticks()

    def on_die_done(self):
        self.status = "close_in_bullets"
        self.state_timer = pygame.time.get_ticks()
        self.snd_floweylaugh.play()

    def on_yeah_whatever_done(self):
        self.status = "post_battle"
        self.state_timer = pygame.time.get_ticks()
        
        # Init Rude Buster
        self.susie_anim_state = "attack"
        self.susie_anim_frame = 0
        self.rude_buster = {"x": self.susie_screen_x + 50, "y": self.susie_screen_y - 10, "step": 0}
        self.snd_laz.play()

    def on_post_battle_done(self):
        # Restore real player drawing and hand control back
        self.player.cutscene_sprite_override = None
        self.player.cutscene_sprite_override_susie = None
        self.flowey_interactable["hidden"] = False
        self.cutscene_mgr.stop_cutscene()


    # ==========================================
    # MATH HELPERS
    # ==========================================

    def _ease_out_cubic(self, t):
        return 1 - (1 - t)**3

    def _ease_in_cubic(self, t):
        return t**3

    def _lerp(self, start, end, t):
        return start + (end - start) * t


    # ==========================================
    # UPDATE LOOP
    # ==========================================

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        # ----------------------------------------------------
        # UNCONDITIONAL ANIMATION TIMERS (Fixes Animation Freezing)
        # ----------------------------------------------------
        if now - self.kris_anim_timer > 100:
            self.kris_anim_timer = now
            if self.kris_anim_state == "battle_idle":
                self.kris_anim_frame = (self.kris_anim_frame + 1) % len(self.kris_idle_sprites)
            elif self.kris_anim_state == "attack":
                if self.kris_anim_frame < len(self.kris_attack_sprites) - 1:
                    self.kris_anim_frame += 1
                else:
                    self.kris_anim_state = "attack_hold"

        if now - self.susie_anim_timer > 100:
            self.susie_anim_timer = now
            if self.susie_anim_state == "battle_idle":
                self.susie_anim_frame = (self.susie_anim_frame + 1) % len(self.susie_idle_sprites)
            elif self.susie_anim_state == "attack":
                if self.susie_anim_frame < len(self.susie_attack_sprites) - 1:
                    self.susie_anim_frame += 1
                else:
                    self.susie_anim_state = "attack_hold"

        # Update Ghosts
        self.ghosts = [g for g in self.ghosts if g.update()]
        
        # Handle Soul Movement
        if self.status in ["wait_spawn_dialogue", "move_bullets", "wait_refuse_dialogue", "wait_die_dialogue"]:
            self._handle_soul_movement()

        # Update spinning bullets
        for b in self.bullets:
            if "sprite_timer" not in b: b["sprite_timer"] = now
            if now - b["sprite_timer"] > 100:
                b["frame"] = (b["frame"] + 1) % 2
                b["sprite_timer"] = now

        # ----------------------------------------------------
        # STATE MACHINE
        # ----------------------------------------------------
        if self.status == "heated_up_delay":
            if elapsed > 2500:
                self.status = "waiting"
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['heated_up'],
                    on_complete=self.on_heated_up_done,
                    actors={"FLOWEY": self.flowey_interactable}
                )

        elif self.status == "pre_battle":
            if elapsed > 600:
                self.status = "waiting"
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['pre_battle'],
                    on_complete=self.on_pre_battle_done,
                    actors={"FLOWEY": self.flowey_interactable}
                )

        elif self.status == "battle_setup":
            self.battle_started = True
            duration = 1000
            t = min(1.0, elapsed / duration)
            ease_t = self._ease_out_cubic(t)

            # Slide entirely in SCREEN SPACE! Camera stays perfectly still.
            self.kris_screen_x = self._lerp(self.original_kris_sx, 150, ease_t)
            self.kris_screen_y = self._lerp(self.original_kris_sy, Constants.HEIGHT // 2 - 50, ease_t)
            
            self.susie_screen_x = self._lerp(self.original_susie_sx, 130, ease_t)
            self.susie_screen_y = self._lerp(self.original_susie_sy, Constants.HEIGHT // 2 + 50, ease_t)

            self.flowey_interactable["hidden"] = True
            self.flowey_screen_x = self._lerp(self.original_flowey_sx, 520, ease_t)
            self.flowey_screen_y = self._lerp(self.original_flowey_sy, Constants.HEIGHT // 2 - 25, ease_t)
            
            # Fetch sprite directly from list if it's an array
            self.flowey_override_sprite = self.context.assets.get_image("spr_flowey_0") if hasattr(self, 'flowey_spin_frames') else self.context.assets.get_image("spr_flowey")[0]

            # Append Ghosts
            if now - getattr(self, 'last_ghost_time', 0) > 32:
                self.last_ghost_time = now
                self.ghosts.append(Ghost(self._get_kris_img(), self.kris_screen_x, self.kris_screen_y))
                self.ghosts.append(Ghost(self._get_susie_img(), self.susie_screen_x, self.susie_screen_y))

            self.darkness_alpha = int(200 * ease_t)
            self.ui_y_offset = self._lerp(150, 0, ease_t)
            self.tp_x_offset = self._lerp(-150, 0, ease_t)

            box_cx = Constants.WIDTH // 2
            box_cy = Constants.HEIGHT // 2 - 50
            current_w = 160 * ease_t
            current_h = 160 * ease_t
            self.box_angle = math.pi * (1 - ease_t)
            self.battle_box = (box_cx, box_cy, current_w, current_h)

            if t >= 1.0:
                self.snd_weapon.play()
                self.status = "battle_intro_anim"
                self.state_timer = now
                self.kris_anim_state = "attack"
                self.kris_anim_frame = 0
                self.susie_anim_state = "attack"
                self.susie_anim_frame = 0

        elif self.status == "battle_intro_anim":
            if elapsed > 700:
                self.kris_anim_state = "battle_idle"
                self.susie_anim_state = "battle_idle"
                
                self.battle_mus.play(-1)
                chest_x = self.kris_screen_x - 30
                chest_y = self.kris_screen_y - 50
                self.soul_x, self.soul_y = chest_x, chest_y
                self.original_soul_x, self.original_soul_y = chest_x, chest_y
                
                self.pulse_timer = now
                self.status = "battle_soul_move"
                self.state_timer = now

        elif self.status == "battle_soul_move":
            t = min(1.0, elapsed / 500)
            ease_t = self._ease_out_cubic(t)
            
            target_x = Constants.WIDTH // 2
            target_y = Constants.HEIGHT // 2 - 50
            
            self.soul_x = self._lerp(self.original_soul_x, target_x, ease_t)
            self.soul_y = self._lerp(self.original_soul_y, target_y, ease_t)

            if t >= 1.0:
                self.status = "waiting"
                self.soul_movement = True
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['battle'],
                    on_complete=self.on_battle_intro_done,
                    actors={"FLOWEY": self.flowey_interactable},
                    is_battle=True
                )

        elif self.status == "spawn_bullets":
            if elapsed < 450:
                speed = 60 / 15 
                for b in self.bullets:
                    b["x"] += math.cos(b["angle"]) * speed
                    b["y"] += math.sin(b["angle"]) * speed
            else:
                self.status = "wait_spawn_dialogue"
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['spawn_bullets'],
                    on_complete=self.on_spawn_bullets_done,
                    actors={"FLOWEY": self.flowey_interactable},
                    is_battle=True
                )

        elif self.status == "move_bullets":
            if elapsed < 600:
                for b in self.bullets:
                    if "target_angle" not in b:
                        dx = self.soul_x - b["x"]
                        dy = self.soul_y - b["y"]
                        b["target_angle"] = math.atan2(dy, dx)
                    
                    b["x"] += math.cos(b["target_angle"]) * 3
                    b["y"] += math.sin(b["target_angle"]) * 3
            else:
                self.status = "wait_refuse_dialogue"
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['refuse_bullets'],
                    on_complete=self.on_refuse_bullets_done,
                    actors={"FLOWEY": self.flowey_interactable},
                    is_battle=True
                )

        elif self.status == "music_stop":
            for b in self.bullets:
                if "target_angle" in b:
                    b["x"] -= math.cos(b["target_angle"]) * 15
                    b["y"] -= math.sin(b["target_angle"]) * 15

            duration = 1000
            t = min(1.0, elapsed / duration)
            ease_t = self._ease_in_cubic(t)
            
            chest_x = self.kris_screen_x - 30
            chest_y = self.kris_screen_y - 50
            self.soul_x = self._lerp(self.original_soul_x, chest_x, ease_t)
            self.soul_y = self._lerp(self.original_soul_y, chest_y, ease_t)
            
            self.darkness_alpha = int(200 * (1 - ease_t))
            self.ui_y_offset = self._lerp(0, 150, ease_t)
            self.tp_x_offset = self._lerp(0, -150, ease_t)
            
            box_cx = Constants.WIDTH // 2
            box_cy = Constants.HEIGHT // 2 - 50
            current_w = 160 * (1 - ease_t)
            current_h = 160 * (1 - ease_t)
            self.box_angle = math.pi * ease_t
            self.battle_box = (box_cx, box_cy, current_w, current_h)
            
            if t >= 1.0:
                self.battle_box = None
                self.pulse_timer = now
                if elapsed > 1500:
                    self.status = "waiting"
                    self.context.dialogue.start_dialogue(
                        self.dialogue_data['music_stop'],
                        on_complete=self.on_music_stop_done,
                        is_battle=True
                    )
        
        elif self.status == "susie_angry":
            if elapsed > 600:
                self.status = "waiting"
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['susie_angry'],
                    on_complete=self.on_susie_angry_done,
                    actors={"FLOWEY": self.flowey_interactable},
                    is_battle=True
                )

        elif self.status == "flowey_attack_setup":
            duration = 1000
            t = min(1.0, elapsed / duration)
            ease_t = self._ease_out_cubic(t)
            
            box_cx = Constants.WIDTH // 2
            box_cy = Constants.HEIGHT // 2 - 50
            current_w = 24 * ease_t
            current_h = 24 * ease_t
            self.box_angle = math.pi * (1 - ease_t)
            self.battle_box = (box_cx, box_cy, current_w, current_h)
            self.darkness_alpha = int(200 * ease_t)
            
            self.soul_x = self._lerp(self.original_soul_x, box_cx, ease_t)
            self.soul_y = self._lerp(self.original_soul_y, box_cy, ease_t)
            
            if t >= 1.0:
                self.status = "spawn_ring"
                self.state_timer = now
                self.snd_pelletcreate.play()
                self.bullets.clear()
        
        elif self.status == "spawn_ring":
            target_bullets = min(36, elapsed // 40)
            while len(self.bullets) < target_bullets:
                index = len(self.bullets)
                angle = (index / 36) * (2 * math.pi)
                bx = self.soul_x + (math.cos(angle) * 100)
                by = self.soul_y + (math.sin(angle) * 100)
                
                self.bullets.append({
                    "x": bx, "y": by,
                    "target_angle": angle + math.pi,
                    "frame": 0
                })
                
            if len(self.bullets) >= 36:
                self.snd_pelletcreate.stop()
                self.status = "wait_die_dialogue"
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['die'],
                    on_complete=self.on_die_done,
                    actors={"FLOWEY": self.flowey_interactable},
                    is_battle=True
                )

        elif self.status == "close_in_bullets":
            if elapsed < 1050: 
                for b in self.bullets:
                    b["x"] += math.cos(b["target_angle"]) * 1
                    b["y"] += math.sin(b["target_angle"]) * 1
            else:
                self.snd_floweylaugh.stop()
                self.status = "waiting"
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['yeah_whatever'],
                    on_complete=self.on_yeah_whatever_done,
                    is_battle=True
                )

        elif self.status == "post_battle":
            if self.rude_buster:
                dx = (self.flowey_screen_x - (self.susie_screen_x + 50)) / 15
                dy = (self.flowey_screen_y - (self.susie_screen_y - 10)) / 15
                
                step = min(15, elapsed // 20)
                self.rude_buster["x"] += dx * (step - self.rude_buster["step"])
                self.rude_buster["y"] += dy * (step - self.rude_buster["step"])
                self.rude_buster["step"] = step
                self.rude_buster["frame"] = step % 7
                
                if step % 2 == 0:
                    ghost_img = self.rude_buster_sprites[self.rude_buster["frame"]]
                    self.ghosts.append(Ghost(ghost_img, self.rude_buster["x"], self.rude_buster["y"]))
                
                if step == 7 and len(self.bullets) > 0:
                    import random
                    for b in self.bullets:
                        b["vx"] = random.uniform(15, 30)
                        b["vy"] = random.uniform(-15, 15)
                
                if step >= 15:
                    self.rude_buster = None
                    self.snd_floweyhit.play()
                    self.flowey_knockout = True
            
            if len(self.bullets) > 0 and "vx" in self.bullets[0]:
                for b in self.bullets:
                    b["x"] += b["vx"]
                    b["y"] += b["vy"]
            
            if hasattr(self, 'flowey_knockout') and self.flowey_knockout:
                self.flowey_screen_x += 30
                self.flowey_screen_y -= 15
                self.flowey_angle -= 45 
                
            if elapsed > 1500:
                self.battle_box = None
                self.darkness_alpha = max(0, self.darkness_alpha - 5)
                
                t = min(1.0, (elapsed - 1500) / 1000)
                ease_t = self._ease_out_cubic(t)
                
                # Slide characters back to their original screen coordinates!
                self.kris_screen_x = self._lerp(150, self.original_kris_sx, ease_t)
                self.kris_screen_y = self._lerp(Constants.HEIGHT // 2 - 50, self.original_kris_sy, ease_t)
                self.susie_screen_x = self._lerp(130, self.original_susie_sx, ease_t)
                self.susie_screen_y = self._lerp(Constants.HEIGHT // 2 + 50, self.original_susie_sy, ease_t)
                
                # Update their animations to face right again
                self.kris_anim_state = "overworld"
                self.susie_anim_state = "overworld"
                
                if elapsed > 4000:
                    self.status = "waiting"
                    self.battle_started = False
                    self.context.dialogue.start_dialogue(
                        self.dialogue_data['post_battle'],
                        on_complete=self.on_post_battle_done
                    )

    def clear_bullets(self, mode="backwards"):
        pass

    def _handle_soul_movement(self):
        speed = 4
        if self.context.inputs.is_pressed(Action.UP): self.soul_y -= speed
        if self.context.inputs.is_pressed(Action.DOWN): self.soul_y += speed
        if self.context.inputs.is_pressed(Action.LEFT): self.soul_x -= speed
        if self.context.inputs.is_pressed(Action.RIGHT): self.soul_x += speed
        
        if self.battle_box:
            cx, cy, w, h = self.battle_box
            min_x = cx - (w/2) + 12
            max_x = cx + (w/2) - 12
            min_y = cy - (h/2) + 12
            max_y = cy + (h/2) - 12
            
            self.soul_x = max(min_x, min(self.soul_x, max_x))
            self.soul_y = max(min_y, min(self.soul_y, max_y))

    def _init_bullet_spread(self):
        self.bullets = []
        num_bullets = 4
        for i in range(num_bullets):
            fraction = i / (num_bullets - 1)
            angle = -(math.pi / 4) + ((math.pi / 2) * fraction)
            self.bullets.append({
                "x": self.flowey_screen_x,
                "y": self.flowey_screen_y,
                "angle": angle,
                "frame": 0
            })

    def _get_kris_img(self):
        if self.kris_anim_state == "overworld": 
            return self.kris_sprites["right"][0]
        if self.kris_anim_state == "battle_idle": 
            frame = self.kris_anim_frame % len(self.kris_idle_sprites)
            return self.kris_idle_sprites[frame]
        
        frame = min(self.kris_anim_frame, len(self.kris_attack_sprites) - 1)
        return self.kris_attack_sprites[frame]

    def _get_susie_img(self):
        if self.susie_anim_state == "overworld": 
            return self.susie_sprites["right"][0]
        if self.susie_anim_state == "battle_idle": 
            frame = self.susie_anim_frame % len(self.susie_idle_sprites)
            return self.susie_idle_sprites[frame]
            
        frame = min(self.susie_anim_frame, len(self.susie_attack_sprites) - 1)
        return self.susie_attack_sprites[frame]


    # ==========================================
    # DRAW LOOP (Pure Screen Space, No Camera Hacks!)
    # ==========================================

    def draw(self, surface, camera):
        # 1. Dark Overlay 
        if self.darkness_alpha > 0:
            dark_surf = pygame.Surface((Constants.WIDTH, Constants.HEIGHT), pygame.SRCALPHA)
            dark_surf.fill((0, 0, 0, self.darkness_alpha))
            surface.blit(dark_surf, (0, 0))

        # 2. Battle Box & Box Ghosts
        if self.battle_box:
            cx, cy, w, h = self.battle_box
            
            def _get_rect_points(cx, cy, w, h, angle):
                hw, hh = w/2, h/2
                corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
                pts = []
                for ox, oy in corners:
                    rx = ox * math.cos(angle) - oy * math.sin(angle)
                    ry = ox * math.sin(angle) + oy * math.cos(angle)
                    pts.append((cx + rx, cy + ry))
                return pts

            pts = _get_rect_points(cx, cy, w, h, self.box_angle)
            pygame.draw.polygon(surface, (0, 0, 0), pts) 
            pygame.draw.polygon(surface, (0, 255, 0), pts, 4) 
            
            if self.status in ["battle_setup", "music_stop", "flowey_attack_setup"]:
                ghost_pts = _get_rect_points(cx, cy, w + 10, h + 10, self.box_angle)
                pygame.draw.polygon(surface, (0, 100, 0), ghost_pts, 2)

        # 3. Ghosts (Kris/Susie slides)
        for g in self.ghosts:
            g.draw(surface) # Draws entirely in screen-space!

        # 4. Characters
        if self.status != "pilot":
            # Draw Kris
            kris_img = self._get_kris_img()
            k_rect = kris_img.get_rect(midbottom=(self.kris_screen_x, self.kris_screen_y + 2))
            surface.blit(kris_img, k_rect)
            
            # Draw Susie
            susie_img = self._get_susie_img()
            s_rect = susie_img.get_rect(midbottom=(self.susie_screen_x, self.susie_screen_y))
            surface.blit(susie_img, s_rect)

        # 5. Flowey Override
        if self.flowey_override_sprite and self.flowey_interactable.get("hidden", False):
            rotated_flowey = pygame.transform.rotate(self.flowey_override_sprite, self.flowey_angle)
            f_rect = rotated_flowey.get_rect(center=(self.flowey_screen_x, self.flowey_screen_y))
            surface.blit(rotated_flowey, f_rect)

        # 6. Bullets
        for b in self.bullets:
            bullet_img = self.flowey_bullet_sprites[b["frame"]]
            b_rect = bullet_img.get_rect(center=(b["x"], b["y"]))
            surface.blit(bullet_img, b_rect)

        # 7. SOUL
        if self.status not in ["pilot", "heated_up_delay", "pre_battle", "battle_setup", "post_battle"]:
            soul_rect = self.player_sprite.get_rect(center=(self.soul_x, self.soul_y))
            surface.blit(self.player_sprite, soul_rect)
            
            if now := pygame.time.get_ticks():
                pulse_elapsed = now - self.pulse_timer
                if pulse_elapsed < 600:
                    t = pulse_elapsed / 600
                    scale = 1 + (1.5 * t)
                    alpha = int(255 * (1 - t))
                    
                    w, h = self.player_sprite.get_size()
                    scaled_soul = pygame.transform.scale(self.player_sprite, (int(w * scale), int(h * scale)))
                    scaled_soul.set_alpha(alpha)
                    
                    p_rect = scaled_soul.get_rect(center=(self.soul_x, self.soul_y))
                    surface.blit(scaled_soul, p_rect)

        # 8. Rude Buster
        if self.rude_buster:
            buster_img = self.rude_buster_sprites[self.rude_buster["frame"]]
            r_rect = buster_img.get_rect(center=(self.rude_buster["x"], self.rude_buster["y"]))
            surface.blit(buster_img, r_rect)

        # 9. Battle UI
        if self.battle_started:
            ui_x = Constants.WIDTH // 2
            ui_y = Constants.HEIGHT + self.ui_y_offset
            ui_rect = self.battle_lower_ui.get_rect(midbottom=(ui_x, ui_y))
            surface.blit(self.battle_lower_ui, ui_rect)
            
            tp_x = 10 + self.tp_x_offset
            tp_rect = self.battle_tp_ui.get_rect(topleft=(tp_x, 50))
            surface.blit(self.battle_tp_ui, tp_rect)


    def _preload_sprites(self):
        assets = self.context.assets
        
        self.kris_sprites = assets.get_image("kris")
        self.susie_sprites = assets.get_image("susie")
        
        self.kris_attack_sprites = assets.get_image(f"spr_krisb_attack")
        self.susie_attack_sprites = assets.get_image(f"spr_susieb_attack")
        self.kris_idle_sprites = assets.get_image(f"spr_krisb_idle")
        self.susie_idle_sprites = assets.get_image(f"spr_susieb_idle")
        self.flowey_bullet_sprites = assets.get_image(f"spr_flowey_pellet")
        self.rude_buster_sprites = assets.get_image(f"spr_rudebuster_beam")
        
        self.player_sprite = assets.get_image("spr_soul")

        # Sound effects & musics
        self.snd_laz = assets.get_sfx("snd_laz_c")
        self.snd_weapon = assets.get_sfx("snd_weaponpull")
        self.snd_pelletcreate = assets.get_sfx("snd_floweypelletscreate")
        self.snd_floweylaugh = assets.get_sfx("snd_floweylaugh")
        self.snd_floweyhit = assets.get_sfx("snd_floweyhurt")
        
        self.flowey_music = pygame.mixer.Sound("assets/sfx/musics/mus_flowey.ogg")
        self.battle_mus = pygame.mixer.Sound("assets/sfx/musics/battle.ogg")

        self.battle_lower_ui = assets.get_image("flowey_fight_lower_ui")
        self.battle_tp_ui = assets.get_image("flowey_fight_tp_bar")