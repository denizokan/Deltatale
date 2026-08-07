import pygame, sys
from pygame import mixer
from src.events.cutscene import Cutscene

class FirstRoomCutscene(Cutscene):
    def __init__(self, context, cutscene_mgr):
        self.context = context
        self.cutscene_mgr = cutscene_mgr
        self.cutscene_mgr.blocks_player = True
    
        try:
            self.dialogue_data = self.cutscene_mgr.load_json("first_room")
        except RuntimeError as e:
            print(f"An error has occured: {e}")
            pygame.quit()
            sys.exit(1)

        self.kris_spawn_x = 270
        self.kris_spawn_y = 220
        self.susie_spawn_x = 330
        self.susie_spawn_y = 220

        self.kris_sprites = [self.context.assets.get_image("spr_dkris_ground")[0], self.context.assets.get_image("spr_dkris_ground")[1], self.context.assets.get_image("spr_dkris_ground")[2], self.context.assets.get_image("kris")["down"][0], self.context.assets.get_image("kris")["right"][0]]
        self.susie_sprites = [self.context.assets.get_image("susie")["down"][0], self.context.assets.get_image("susie")["left"][0]]
        self.susie_attack_sprites = [
            self.context.assets.get_image("spr_susieb_attack")[0],
            self.context.assets.get_image("spr_susieb_attack")[1],
            self.context.assets.get_image("spr_susieb_attack")[2],
            self.context.assets.get_image("spr_susieb_attack")[3],
            self.context.assets.get_image("spr_susieb_attack")[4],
            self.context.assets.get_image("spr_susieb_attack")[5]
        ]

        self.player = self.context.world.player
        self.player.x, self.player.y = self.kris_spawn_x, self.kris_spawn_y
        self.player.cutscene_sprite_override = self.kris_sprites[0]

        self.player.cutscene_sprite_override = self.kris_sprites[0] 
        self.player.cutscene_sprite_override_susie = self.susie_sprites[1]
        
        self.status = "pilot"
        self.state_timer = pygame.time.get_ticks()
        self.anim_frame = 0
        
        self.context.dialogue.start_dialogue(
            self.dialogue_data['pilot'],
            on_complete=self.on_pilot_done
        )


    # --- Callbacks to change states ---
    
    def on_pilot_done(self):
        self.status = "waking_up_delay"
        self.state_timer = pygame.time.get_ticks()
        self.anim_frame = 0
        self.context.transitions.fade_from_black(speed=12)
        
    def on_wakeup_dialogue_done(self):
        self.status = "axe_realization"
        self.state_timer = pygame.time.get_ticks()
        self.anim_frame = 0
        self.context.assets.get_sfx("snd_laz_c").play()
        
    def on_axe_dialogue_done(self):
        self.status = "after_realization"
        self.state_timer = pygame.time.get_ticks()
        self.anim_frame = 0

    def on_after_dialogue_done(self):
        self.status = "cutscene_end"
        self.state_timer = pygame.time.get_ticks()
        self.anim_frame = 0


    # --- Update loop ---

    def update(self):
        now = pygame.time.get_ticks()
        elapsed_time = now - self.state_timer

        # PHASE 2: Waking up
        if self.status == "waking_up_delay":
            if elapsed_time > 2000 and self.anim_frame == 0:
                self.player.cutscene_sprite_override = self.kris_sprites[1]
                self.anim_frame = 1
                
            elif elapsed_time > 2400 and self.anim_frame == 1:
                self.player.cutscene_sprite_override = self.kris_sprites[2]
                self.anim_frame = 2

            elif elapsed_time > 2800 and self.anim_frame == 2:
                self.player.cutscene_sprite_override = self.kris_sprites[3]
                self.anim_frame = 3

            elif elapsed_time > 3200 and self.anim_frame == 3:
                self.player.cutscene_sprite_override = self.kris_sprites[4]
                self.anim_frame = 4
                
            elif elapsed_time > 3600 and self.anim_frame == 4:
                self.status = "waiting_for_dialogue" 
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['waking_up'],
                    on_complete=self.on_wakeup_dialogue_done
                )

        # PHASE 3: Susie Attack Animation
        elif self.status == "axe_realization":
            if elapsed_time > (self.anim_frame * 100) and self.anim_frame < 6:
                self.player.cutscene_sprite_override_susie = self.susie_attack_sprites[self.anim_frame]
                self.anim_frame += 1
            
            elif elapsed_time > 500 and self.anim_frame == 6:
                self.status = "waiting_for_dialogue"
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['axe_realization'],
                    on_complete=self.on_axe_dialogue_done
                )
                
        # PHASE 4: After Realization
        elif self.status == "after_realization":
            if elapsed_time > 100 and self.anim_frame == 0:
                self.player.cutscene_sprite_override_susie = self.susie_sprites[1]
                self.anim_frame = 1
                
                self.status = "waiting_for_dialogue"
                self.context.dialogue.start_dialogue(
                    self.dialogue_data['after_realization'],
                    on_complete=self.on_after_dialogue_done
                )

        # PHASE 5: Clean up and Stop Cutscene
        elif self.status == "cutscene_end":
            if self.anim_frame == 0:
                self.player.cutscene_sprite_override = self.kris_sprites[3]
                self.player.cutscene_sprite_override_susie = None
                
                self.player._move_susie_behind_kris(
                    susie_start_coords=(self.susie_spawn_x, self.susie_spawn_y), 
                    kris_facing="down"
                )
                self.anim_frame = 1
                
            elif self.anim_frame == 1:
                if self.player.state == "SUSIE_CINEMATIC":
                    self.player._susie_walk_step()
                else:
                    self.player.cutscene_sprite_override = None
                    self.cutscene_mgr.stop_cutscene()


    def draw(self, surface, camera):
        pass