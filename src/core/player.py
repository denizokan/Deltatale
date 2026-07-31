import pygame
from src.core.enums import Action
from src.core.constants import Constants

class Player:
    """
    Handles player overworld movement and tracks stats.
    """

    def __init__(self, start_x, start_y, start_facing, asset_manager, input_manager):
        self.x = start_x
        self.y = start_y
        self.facing = start_facing

        self.asset_manager = asset_manager
        self.input_manager = input_manager

        self.speed = Constants.PLAYER_SPEED

        # Stats (TODO: Scale later)
        self.level = 1
        self.exp = 0
        self.hp = 20
        self.money = 0
        # -----

        self.state = "NORMAL"
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 4

        self.follow_delay = 15
        self.history = [(self.x, self.y, self.facing, self.anim_frame)] * self.follow_delay

        self.kris_sprites = {
            "down": self.asset_manager.get_image("kris")["down"],
            "up": self.asset_manager.get_image("kris")["up"],
            "left": self.asset_manager.get_image("kris")["left"],
            "right": self.asset_manager.get_image("kris")["right"]
        }
        
        self.susie_sprites = {
            "down": self.asset_manager.get_image("susie")["down"],
            "up": self.asset_manager.get_image("susie")["up"],
            "left": self.asset_manager.get_image("susie")["left"],
            "right": self.asset_manager.get_image("susie")["right"]
        }

        self.sprite_offsets = {
            "kris": (0, 2),
            "susie": (0, 0)
        }


    def update(self, input_mgr, current_room):
        """Handles inputs and modifies the player sprite."""
        if self.state == "SUSIE_CINEMATIC":
            self._susie_walk_step()
            return
        
        if input_mgr.is_just_pressed(Action.CONFIRM):
            current_room.check_interactable(self.x, self.y, self.facing)

        if input_mgr.is_just_pressed(Action.MENU):
            return "MENU"
        
        dx, dy = 0, 0
        new_facing = self.facing

        active_key = input_mgr.get_active_direction()
        self.anim_speed = 4
        speed_mult = 1

        if input_mgr.is_pressed(Action.CANCEL):
            self.anim_speed = 2
            speed_mult = 1.6

        if active_key == pygame.K_UP:
            dy = -self.speed * speed_mult
            new_facing = "up"
        elif active_key == pygame.K_DOWN:
            dy = self.speed * speed_mult
            new_facing = "down"
        elif active_key == pygame.K_LEFT:
            dx = -self.speed * speed_mult
            new_facing = "left"
        elif active_key == pygame.K_RIGHT:
            dx = self.speed * speed_mult
            new_facing = "right"

        if (dx != 0 or dy != 0):
            self.facing = new_facing
            self.move(dx, dy, current_room)
        else:
            self.anim_frame = 0
            self.anim_timer = 0
            self.history[0] = (self.history[0][0], self.history[0][1], self.history[0][2], 0)

    
    def move(self, dx, dy, current_room):
        """Records history, applies movement, and triggers the draw sequence."""
        target_x = self.x + dx
        target_y = self.y + dy

        moved = False

        if not current_room.is_position_free(target_x, self.y):
            self.anim_frame = 0
            self.history[0] = (self.history[0][0], self.history[0][1], self.history[0][2], 0)

        if dx != 0 and current_room.is_position_free(target_x, self.y):
            self.x += dx
            moved = True

        if dy != 0 and current_room.is_position_free(self.x, target_y):
            self.y += dy
            moved = True

        if moved:
            self.history.append((self.x, self.y, self.facing, self.anim_frame))
            if len(self.history) > self.follow_delay:
                self.history.pop(0)

            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame > 3:
                    self.anim_frame = 0
            
        current_room.check_exit(self.x, self.y)
        current_room.check_trigger(self.x, self.y)


    def draw(self, surface, camera):
        """Updates the canvas coordinates and images for all party members."""
        if self.state == "SUSIE_CINEMATIC":
            sx = self._susie_x
            sy = self._susie_y
            s_facing = self._susie_facing
            s_frame = self.anim_frame
        else:
            sx, sy, s_facing, s_frame = self.history[0]

        kris_img = self.kris_sprites[self.facing][self.anim_frame]
        susie_img = self.susie_sprites[s_facing][s_frame]

        kris_rect = kris_img.get_rect(midbottom=(self.x - camera.x, self.y - camera.y + self.sprite_offsets["kris"][1]))
        susie_rect = susie_img.get_rect(midbottom=(sx - camera.x, sy - camera.y + self.sprite_offsets["susie"][1]))

        if self.y > sy: # Kris is lower down on screen
            surface.blit(susie_img, susie_rect)
            surface.blit(kris_img, kris_rect)
        else:
            surface.blit(kris_img, kris_rect)
            surface.blit(susie_img, susie_rect)


    def _move_susie_behind_kris(self, susie_start_coords, kris_facing="down", offset=30):
        """Calculates the target coordinates and begins the cinematic walk loop."""
        self.state = "SUSIE_CINEMATIC"
        self.facing = kris_facing

        if self.facing == "down":
            self._target_x = self.x
            self._target_y = self.y - offset
        elif self.facing == "up":
            self._target_x = self.x
            self._target_y = self.y + offset
        elif self.facing == "right":
            self._target_x = self.x - offset
            self._target_y = self.y
        elif self.facing == "left":
            self._target_x = self.x + offset
            self._target_y = self.y

        self._susie_x, self._susie_y = susie_start_coords
        self.anim_frame = 0
        self.anim_timer = 0


    def _susie_walk_step(self):
        """Runs once per frame. Moves Susie closer to the target and ticks her animation."""
        reached_y = False
        reached_x = False
        
        if abs(self._susie_y - self._target_y) > self.speed:
            if self._susie_y < self._target_y:
                self._susie_y += self.speed
                self._susie_facing = "down"
            else:
                self._susie_y -= self.speed
                self._susie_facing = "up"
        else:
            self._susie_y = self._target_y
            reached_y = True
            
        if reached_y:
            if abs(self._susie_x - self._target_x) > self.speed:
                if self._susie_x < self._target_x:
                    self._susie_x += self.speed
                    self._susie_facing = "right"
                else:
                    self._susie_x -= self.speed
                    self._susie_facing = "left"
            else:
                self._susie_x = self._target_x
                reached_x = True
                
        if not (reached_x and reached_y):
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame > 3:
                    self.anim_frame = 0
        else:
            self.anim_frame = 0
            new_history = []
            for i in range(self.follow_delay):
                t = i / (self.follow_delay - 1)
                hist_x = self._target_x + (self.x - self._target_x) * t
                hist_y = self._target_y + (self.y - self._target_y) * t
                new_history.append((hist_x, hist_y, self.facing, 0))
            self.history = new_history

            self.state = "NORMAL"