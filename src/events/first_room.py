import pygame, sys
from src.events.cutscene import Cutscene
from src.events.cutscene_actions import (
    DialogueAction, WaitAction, PlaySoundAction, 
    ParallelAction, AnimateAction, CallAction, CustomLoopAction
)

class FirstRoomCutscene(Cutscene):
    def __init__(self, context, cutscene_mgr):
        super().__init__()
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

        self.preload_sprites()
        
        self.action_queue = [
            DialogueAction(self.context, self.dialogue_data['pilot']),
            
            CallAction(self.context.transitions.fade_from_black, speed=12),
            WaitAction(2000),
            
            AnimateAction(self.player, "cutscene_sprite_override", self.kris_sprites[1:5], delay_ms=400),
            
            DialogueAction(self.context, self.dialogue_data['waking_up']),
            
            ParallelAction(
                PlaySoundAction(self.context.assets.get_sfx("snd_laz_c")),
                AnimateAction(self.player, "cutscene_sprite_override_susie", self.susie_attack_sprites, delay_ms=100)
            ),
            
            DialogueAction(self.context, self.dialogue_data['axe_realization']),
            
            WaitAction(100),
            CallAction(setattr, self.player, "cutscene_sprite_override_susie", self.susie_sprites[1]),
            DialogueAction(self.context, self.dialogue_data['after_realization']),
            
            CallAction(self.setup_susie_walk),
            CustomLoopAction(
                update_func=self.update_susie_walk,
                check_done_func=lambda: self.player.state != "SUSIE_CINEMATIC"
            ),
            
            CallAction(self.finish_cutscene)
        ]

    # --- Helpers ---

    def setup_susie_walk(self):
        """Called once to setup the final sequence."""
        self.player.cutscene_sprite_override = self.kris_sprites[3]
        self.player.cutscene_sprite_override_susie = None
        self.player._move_susie_behind_kris(
            susie_start_coords=(self.susie_spawn_x, self.susie_spawn_y), 
            kris_facing="down"
        )

    def update_susie_walk(self):
        """Called every frame by the CustomLoopAction."""
        if self.player.state == "SUSIE_CINEMATIC":
            self.player._susie_walk_step()

    def finish_cutscene(self):
        """Called once at the very end."""
        self.player.cutscene_sprite_override = None
        self.cutscene_mgr.stop_cutscene()

    def draw(self, surface, camera):
        pass


    def preload_sprites(self):
        self.kris_sprites = [
            self.context.assets.get_image("spr_dkris_ground")[0], 
            self.context.assets.get_image("spr_dkris_ground")[1], 
            self.context.assets.get_image("spr_dkris_ground")[2], 
            self.context.assets.get_image("kris")["down"][0], 
            self.context.assets.get_image("kris")["right"][0]
        ]
        self.susie_sprites = [
            self.context.assets.get_image("susie")["down"][0], 
            self.context.assets.get_image("susie")["left"][0]
        ]
        
        self.susie_attack_sprites = [
            self.context.assets.get_image("spr_susieb_attack")[i] for i in range(6)
        ]
        
        self.player = self.context.world.player
        self.player.x, self.player.y = self.kris_spawn_x, self.kris_spawn_y
        self.player.cutscene_sprite_override = self.kris_sprites[0] 
        self.player.cutscene_sprite_override_susie = self.susie_sprites[1]