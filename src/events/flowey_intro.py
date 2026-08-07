import pygame, sys
import math
from src.core.constants import Constants, Color
from src.core.enums import Action
from src.events.cutscene import Cutscene
from src.events.cutscene_actions import WaitAction, DialogueAction, PlaySoundAction, ParallelAction, AnimateAction, CallAction, CustomLoopAction, CutsceneSequence, SlideAction

class FloweyIntroCutscene(Cutscene):
    def __init__(self, context, cutscene_mgr):
        super().__init__()
        self.context = context
        self.cutscene_mgr = cutscene_mgr
        self.flowey_interactable = self.context.world.current_room.interactables[0]
        self.cutscene_mgr.blocks_player = True
        self.battle_started = False

        try:
            self.dialogue_data = self.cutscene_mgr.load_json("flowey_first_interaction")
        except RuntimeError as e:
            print(f"An error has occured: {e}")
            pygame.quit()
            sys.exit(1)

        # --- Visual State Variables ---
        self.bg_darkness = 0
        
        # Battle Box State
        self.box_active = False
        self.box_current_w = 0
        self.box_current_h = 0
        self.box_angle = 0
        self.box_target_w = 160
        self.box_target_h = 160
        self.box_ghosts = []
        
        # Bullet State
        self.active_bullets = []
        self.bullet_anim_timer = 0
        self.bullet_sprite_index = 0

        # Character References
        self.player = self.context.world.player
        sx, sy, s_facing, _ = self.player.history[0]
        self.player._susie_x = sx
        self.player._susie_y = sy
        self.player._susie_facing = s_facing
        self.player.state = "SUSIE_CINEMATIC"

        # SOUL State Variables
        self.soul_visible = False
        self.soul_x = 0
        self.soul_y = 0
        
        # Pulse State
        self.is_pulsing = False
        self.pulse_frame = 0
        self.pulse_timer = 0
        
        self.preload_sprites()

        self.action_queue = [
            PlaySoundAction(self.flowey_music, loops=-1),
            DialogueAction(self.context, self.dialogue_data['greeting'], actors={"FLOWEY": self.flowey_interactable}),
            ParallelAction(
                CallAction(self.flowey_music.fadeout, 1500),
                WaitAction(2500)
            ),

            DialogueAction(self.context, self.dialogue_data['heated_up'], actors={"FLOWEY": self.flowey_interactable}),
            ParallelAction(
                PlaySoundAction(self.snd_laz),
                AnimateAction(self.player, "cutscene_sprite_override_susie", self.susie_attack_sprites, delay_ms=100)
            ),
            
            DialogueAction(self.context, self.dialogue_data['pre_battle']),
            WaitAction(100),

            # --- 1. SLIDE EVERYONE INTO POSITION ---
            ParallelAction(
                SlideAction(self.player, "x", "y", (150, Constants.HEIGHT // 2 - 50), 300),
                SlideAction(self.player, "_susie_x", "_susie_y", (130, Constants.HEIGHT // 2 + 50), 300),
                SlideAction(self.flowey_interactable, "x", "y", (520, Constants.HEIGHT // 2 - 25), 300),
            ),

            # --- 2. DRAW SWORDS & PLAY ANIMATIONS ---
            CallAction(self.snd_weapon.play),
            ParallelAction(
                AnimateAction(self.player, "cutscene_sprite_override", self.kris_attack_sprites, delay_ms=100),
                AnimateAction(self.player, "cutscene_sprite_override_susie", self.susie_attack_sprites, delay_ms=100)
            ),
            
            # --- 3. START MUSIC & OPEN BATTLE BOX ---
            PlaySoundAction(self.battle_mus, loops=-1),
            CallAction(self.start_box_anim),
            CustomLoopAction(self.update_box_anim),

            # --- 4. SOUL EXTRACTION ---
            CallAction(self.setup_soul_spawn),
            SlideAction(self, "soul_x", "soul_y", (Constants.WIDTH // 2, Constants.HEIGHT // 2 - 50), 400),
            CallAction(self.trigger_soul_pulse),

            # --- 5. BATTLE PHASE ---
            CallAction(self.setup_battle),
            ParallelAction(
                # Loop 1: Constant SOUL movement and constraints
                CustomLoopAction(
                    update_func=self.update_battle,
                    check_done_func=lambda: not self.battle_started
                ),
                
                # Loop 2: The sequence of Flowey's attacks
                CutsceneSequence([
                    CallAction(self.spawn_bullets),
                    CustomLoopAction(self.update_bullets_popping, lambda: False),
                    DialogueAction(self.context, self.dialogue_data['spawn_bullets'], is_battle=True),
                    
                    CallAction(self.target_bullets_to_soul),
                    CustomLoopAction(self.update_bullets_moving, lambda: False),
                    DialogueAction(self.context, self.dialogue_data['refuse_bullets'], is_battle=True),
                    
                    # Rest of the battle sequence
                ])
            ),

            CallAction(self.finish_cutscene)
        ]


    def draw(self, surface, camera):
        # Darken Background
        if self.bg_darkness > 0:
            dark_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            dark_surf.fill((0, 0, 0, int(self.bg_darkness)))
            surface.blit(dark_surf, (0, 0))

        # Soul Pulse Effect
        if self.soul_visible:
            if self.is_pulsing and self.pulse_frame < len(self.pulse_frames):
                pulse_img = self.pulse_frames[self.pulse_frame]
                pulse_rect = pulse_img.get_rect(center=(int(self.soul_x), int(self.soul_y)))
                surface.blit(pulse_img, pulse_rect)
            
            soul_rect = self.player_sprite.get_rect(center=(int(self.soul_x), int(self.soul_y)))
            surface.blit(self.player_sprite, soul_rect)

        # Draw Battle Box Ghosts
        for ghost in self.box_ghosts:
            pygame.draw.polygon(surface, ghost['color'], ghost['points'], width=4)

        # Draw Main Battle Box
        if self.box_active:
            box_x, box_y = Constants.WIDTH // 2, Constants.HEIGHT // 2 - 50
            
            if self.box_angle == 0:
                rect = pygame.Rect(0, 0, self.box_current_w, self.box_current_h)
                rect.center = (box_x, box_y)
                pygame.draw.rect(surface, Color.BLACK, rect)
                pygame.draw.rect(surface, Color.GREEN, rect, width=4)
            else:
                points = self._get_rotated_corners(box_x, box_y, self.box_current_w, self.box_current_h, self.box_angle)
                pygame.draw.polygon(surface, Color.BLACK, points)
                pygame.draw.polygon(surface, Color.GREEN, points, width=4)

        # Draw Bullets
        if self.active_bullets:
            bullet_img = self.flowey_bullet_sprites[self.bullet_sprite_index]
            for bullet in self.active_bullets:
                bullet_rect = bullet_img.get_rect(center=(int(bullet['x']), int(bullet['y'])))
                surface.blit(bullet_img, bullet_rect)


    # --- Helpers ---

    def setup_battle(self):
        """Sets initial SOUL position and starts the battle state."""
        self.battle_started = True
        self.soul_x = Constants.WIDTH // 2
        self.soul_y = Constants.HEIGHT // 2 - 50


    def update_battle(self):
        if not self.battle_started:
            return

        if self.is_pulsing:
            now = pygame.time.get_ticks()
            if now - self.pulse_timer > 40:
                self.pulse_frame += 1
                self.pulse_timer = now
                if self.pulse_frame >= len(self.pulse_frames):
                    self.is_pulsing = False

        target_x, target_y = self.soul_x, self.soul_y

        if self.context.inputs.is_pressed(Action.UP): target_y -= Constants.SOUL_SPEED
        if self.context.inputs.is_pressed(Action.DOWN): target_y += Constants.SOUL_SPEED
        if self.context.inputs.is_pressed(Action.LEFT): target_x -= Constants.SOUL_SPEED
        if self.context.inputs.is_pressed(Action.RIGHT): target_x += Constants.SOUL_SPEED

        box_center_x = Constants.WIDTH // 2
        box_center_y = Constants.HEIGHT // 2 - 50
        
        soul_radius = 8
        offset = 4 
        
        min_x = (box_center_x - self.box_current_w / 2) + offset + soul_radius
        max_x = (box_center_x + self.box_current_w / 2) - offset - soul_radius
        min_y = (box_center_y - self.box_current_h / 2) + offset + soul_radius
        max_y = (box_center_y + self.box_current_h / 2) - offset - soul_radius

        self.soul_x = max(min_x, min(target_x, max_x))
        self.soul_y = max(min_y, min(target_y, max_y))

        self.bullet_anim_timer += 1
        if self.bullet_anim_timer >= 6:
            self.bullet_sprite_index = (self.bullet_sprite_index + 1) % 2
            self.bullet_anim_timer = 0


    def spawn_bullets(self):
        """Called by Action Queue: Spawns bullets fanning out from Flowey."""
        self.active_bullets = []
        
        spawn_x = self.flowey_interactable.x
        spawn_y = self.flowey_interactable.y
        
        num_bullets = 4
        
        for i in range(num_bullets):
            fraction = i / (num_bullets - 1) 
            start_angle = -(math.pi / 4) 
            total_spread = (math.pi / 2)
            angle = start_angle + (total_spread * fraction)
            
            self.active_bullets.append({
                "x": spawn_x,
                "y": spawn_y,
                "angle": angle,
                "target_angle": 0,
                "state": "popping",
                "pop_distance": 0
            })


    def update_bullets_popping(self):
        """Called by Action Queue: Pushes bullets outward from Flowey."""
        all_popped = True
        speed = 4
        
        for bullet in self.active_bullets:
            if bullet["pop_distance"] < 60:
                bullet["x"] += math.cos(bullet["angle"]) * speed
                bullet["y"] += math.sin(bullet["angle"]) * speed
                bullet["pop_distance"] += speed
                all_popped = False
                
        return all_popped
    

    def target_bullets_to_soul(self):
        """Called by Action Queue: Locks bullet angles onto the player's SOUL."""
        for bullet in self.active_bullets:
            dx = self.soul_x - bullet["x"]
            dy = self.soul_y - bullet["y"]
            bullet["target_angle"] = math.atan2(dy, dx)
            bullet["state"] = "moving"
            bullet["frames_moved"] = 0

    def update_bullets_moving(self):
        """Called by Action Queue: Moves bullets towards the SOUL briefly."""
        all_moved = True
        speed = 3
        max_frames = 30
        
        for bullet in self.active_bullets:
            if bullet["frames_moved"] < max_frames:
                bullet["x"] += math.cos(bullet["target_angle"]) * speed
                bullet["y"] += math.sin(bullet["target_angle"]) * speed
                bullet["frames_moved"] += 1
                all_moved = False
                
        return all_moved


    def setup_soul_spawn(self):
        """Places the SOUL on Kris's chest and makes it visible."""
        self.soul_visible = True
        self.soul_x = self.player.x - 30
        self.soul_y = self.player.y - 50
        
    def trigger_soul_pulse(self):
        """Starts the pulse animation loop."""
        self.is_pulsing = True
        self.pulse_frame = 0
        self.pulse_timer = pygame.time.get_ticks()


    def finish_cutscene(self):
        """Called once at the very end."""
        self.player.cutscene_sprite_override = None
        self.cutscene_mgr.stop_cutscene()
    

    def preload_sprites(self):
        # Player
        self.player_sprite = self.context.assets.get_image("spr_soul")

        self.kris_sprites = [
            self.context.assets.get_image("kris")["up"][0], 
            self.context.assets.get_image("kris")["right"][0]
        ]
        self.susie_sprites = [
            self.context.assets.get_image("susie")["up"][0], 
            self.context.assets.get_image("susie")["right"][0]
        ]

        self.kris_attack_sprites = [
            self.context.assets.get_image("spr_krisb_attack")[i] for i in range(7)
        ]
        
        self.susie_attack_sprites = [
            self.context.assets.get_image("spr_susieb_attack")[i] for i in range(6)
        ]

        self.kris_idle_sprites = [
            self.context.assets.get_image("spr_krisb_idle")[i] for i in range(6)
        ]

        self.susie_idle_sprites = [
            self.context.assets.get_image("spr_susieb_idle")[i] for i in range(4)
        ]

        self.flowey_bullet_sprites = [
            self.context.assets.get_image("spr_flowey_pellet")[i] for i in range(2)
        ]
        for i, sprite in enumerate(self.flowey_bullet_sprites):
            self.flowey_bullet_sprites[i] = pygame.transform.scale_by(sprite, 1)

        self.rude_buster_sprites = [
            self.context.assets.get_image("spr_rudebuster_beam")[i] for i in range(7)
        ]
        
        self.player = self.context.world.player
        self.player.cutscene_sprite_override = self.kris_sprites[0] 
        self.player.cutscene_sprite_override_susie = self.susie_sprites[0]

        self.kris_ghosts = self._generate_faded_ghosts(self.context.assets.get_image("kris")["right"][0])
        self.susie_ghosts = self._generate_faded_ghosts(self.context.assets.get_image("susie")["right"][0])
        self.pulse_frames = self._generate_pulse_frames(self.player_sprite, base_zoom=2, max_zoom=4.5, frames=12)
        self.soul_fade_frames = self._generate_faded_ghosts(self.player_sprite, frames=10)
        self.flowey_spin_frames = self._generate_rotated_frames(self.context.assets.get_image("spr_flowey")[0], frames=8)
        
        self.rude_buster_ghosts = [
            self._generate_faded_ghosts(self.rude_buster_sprites[i], frames=5)
            for i in range(7)
        ]

        # Sound Effects
        self.snd_laz = self.context.assets.get_sfx("snd_laz_c")
        self.snd_weapon = self.context.assets.get_sfx("snd_weaponpull")
        self.snd_pelletcreate = self.context.assets.get_sfx("snd_floweypelletscreate")
        self.snd_floweylaugh = self.context.assets.get_sfx("snd_floweylaugh")
        self.snd_floweyhit = self.context.assets.get_sfx("snd_floweyhurt")
        self.flowey_music = self.context.assets.get_sfx("mus_flowey")
        self.battle_mus = self.context.assets.get_sfx("mus_battle")

        # Battle UI
        self.battle_lower_ui = self.context.assets.get_image("flowey_fight_lower_ui")
        self.battle_tp_ui = self.context.assets.get_image("flowey_fight_tp_bar")


    # --- Image Manipulation Helpers ---

    def _generate_faded_ghosts(self, surface, frames=6):
        """Generates an array of surfaces that gradually fade to 0 opacity."""
        ghosts = []
        for i in range(frames):
            opacity = int(255 * (1.0 - (i / frames)))
            ghost_surf = surface.copy()
            ghost_surf.set_alpha(opacity)
            ghosts.append(ghost_surf)
        return ghosts

    def _generate_pulse_frames(self, surface, base_zoom=2, max_zoom=4.5, frames=12):
        """Generates an expanding, fading pulse effect."""
        pulse_frames = []
        base_w, base_h = surface.get_size()
        
        for i in range(frames):
            t = i / (frames - 1)
            current_zoom = base_zoom + ((max_zoom - base_zoom) * t)
            opacity = int(255 * (1.0 - t))
            
            new_w = int(base_w * current_zoom)
            new_h = int(base_h * current_zoom)
            
            resized = pygame.transform.scale(surface, (new_w, new_h))
            resized.set_alpha(opacity)
            pulse_frames.append(resized)
            
        return pulse_frames

    def _generate_rotated_frames(self, surface, frames=8):
        """Generates an array of rotated sprites."""
        rotated = []
        for i in range(frames):
            angle = i * (360 / frames)
            rot_surf = pygame.transform.rotate(surface, angle)
            rotated.append(rot_surf)
        return rotated

    def _get_rotated_corners(self, cx, cy, w, h, angle):
        """Calculates the 4 corners of a rotated rectangle for Pygame polygon drawing."""
        hw, hh = w / 2, h / 2
        corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        rotated_coords = []
        
        for x_off, y_off in corners:
            rx = x_off * math.cos(angle) - y_off * math.sin(angle)
            ry = x_off * math.sin(angle) + y_off * math.cos(angle)
            rotated_coords.append((cx + rx, cy + ry))
            
        return rotated_coords

    def start_box_anim(self):
        """Called by the queue to initialize the box opening animation."""
        self.box_active = True
        self.box_anim_frame = 0
        self.box_anim_total_frames = 20
        self.box_ghosts.clear()

    def update_box_anim(self):
        """Called every tick by CustomLoopAction until the box is fully formed."""
        if self.box_anim_frame > self.box_anim_total_frames:
            self.box_angle = 0
            self.box_ghosts.clear()
            return True

        t = self.box_anim_frame / self.box_anim_total_frames
        ease_t = 1 - (1 - t)**3

        self.bg_darkness = 200 * ease_t
        self.box_current_w = self.box_target_w * ease_t
        self.box_current_h = self.box_target_h * ease_t
        self.box_angle = math.pi * (1 - ease_t)

        box_x, box_y = Constants.WIDTH // 2, Constants.HEIGHT // 2 - 50
        current_corners = self._get_rotated_corners(box_x, box_y, self.box_current_w, self.box_current_h, self.box_angle)

        if t < 0.35 and self.box_anim_frame % 2 == 0:
            self.box_ghosts.append({
                'points': current_corners,
                'color': [0, 255, 0],
                'life': 5
            })

        for ghost in reversed(self.box_ghosts):
            ghost['life'] -= 1
            ghost['color'][1] = max(0, ghost['color'][1] - 50)
            if ghost['life'] <= 0:
                self.box_ghosts.remove(ghost)

        self.box_anim_frame += 1
        return False