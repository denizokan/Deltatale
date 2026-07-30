from tkinter import PhotoImage
from src.core.enums import Action

class Player:
    """
    Handles player overworld movement and tracks stats.
    """

    def __init__(self, main_game, start_x, start_y, start_facing):
        self.game = main_game
        self.x = start_x
        self.y = start_y
        self.facing = start_facing

        self.speed = self.game.constants.PLAYER_SPEED

        # Stats (TODO: Scale later)
        self.level = 1
        self.exp = 0
        self.hp = 20
        self.money = 0
        # -----

        self.active_characters = []
        self.active_ui_elements = []

        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 4

        self.follow_delay = 15
        self.history = [(self.x, self.y, self.facing, self.anim_frame)] * self.follow_delay

        self.kris_sprites = {
            "down": [PhotoImage(file="sprites/characters/kris/walk/spr_krisd_0.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisd_1.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisd_2.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisd_3.png").zoom(2)],
            "up": [PhotoImage(file="sprites/characters/kris/walk/spr_krisu_0.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisu_1.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisu_2.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisu_3.png").zoom(2)],
            "left": [PhotoImage(file="sprites/characters/kris/walk/spr_krisl_0.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisl_1.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisl_2.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisl_3.png").zoom(2)],
            "right": [PhotoImage(file="sprites/characters/kris/walk/spr_krisr_0.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisr_1.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisr_2.png").zoom(2), PhotoImage(file="sprites/characters/kris/walk/spr_krisr_3.png").zoom(2)]
        }
        
        self.susie_sprites = {
            "down": [PhotoImage(file="sprites/characters/susie/walk/spr_susied_0.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susied_1.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susied_2.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susied_3.png").zoom(2)],
            "up": [PhotoImage(file="sprites/characters/susie/walk/spr_susieu_0.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susieu_1.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susieu_2.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susieu_3.png").zoom(2)],
            "left": [PhotoImage(file="sprites/characters/susie/walk/spr_susiel_0.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susiel_1.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susiel_2.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susiel_3.png").zoom(2)],
            "right": [PhotoImage(file="sprites/characters/susie/walk/spr_susier_0.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susier_1.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susier_2.png").zoom(2), PhotoImage(file="sprites/characters/susie/walk/spr_susier_3.png").zoom(2)]
        }

        kris_sprite = self.game.canvas.create_image(self.x, self.y, image=self.kris_sprites[self.facing][0], anchor="s")
        susie_sprite = self.game.canvas.create_image(self.x, self.y, image=self.susie_sprites[self.facing][0], anchor="s")

        self.game.canvas.tag_raise(kris_sprite)

        self.active_characters.extend([kris_sprite, susie_sprite])


    def update(self, input_mgr):
        """Handles inputs and modifies the player sprite."""      
        if self.game.transition.is_transitioning or self.game.current_room.is_paused:
            return

        if input_mgr.is_just_pressed(Action.CONFIRM):
            self.game.current_room.check_interactable()

        if input_mgr.is_just_pressed(Action.MENU):
            self.game.menu_screen.open_menu(index=0)
        
        dx, dy = 0, 0
        new_facing = self.facing

        active_key = input_mgr.get_active_direction()
        self.anim_speed = 4
        speed_mult = 1

        if input_mgr.is_pressed(Action.CANCEL):
            self.anim_speed = 2
            speed_mult = 1.6

        if active_key == "Up":
            dy = -self.speed * speed_mult
            new_facing = "up"
        elif active_key == "Down":
            dy = self.speed * speed_mult
            new_facing = "down"
        elif active_key == "Left":
            dx = -self.speed * speed_mult
            new_facing = "left"
        elif active_key == "Right":
            dx = self.speed * speed_mult
            new_facing = "right"

        if (dx != 0 or dy != 0):
            self.facing = new_facing
            self.move(dx, dy)
        else:
            self.anim_frame = 0
            self.anim_timer = 0
            sx, sy, s_facing, s_frame = self.history[0]
            self.game.canvas.itemconfig(self.active_characters[0], image=self.kris_sprites[self.facing][0])
            self.game.canvas.itemconfig(self.active_characters[1], image=self.susie_sprites[s_facing][0])

    
    def move(self, dx, dy):
        """Records history, applies movement, and triggers the draw sequence."""
        target_x = self.x + dx
        target_y = self.y + dy

        moved = False

        if not self.game.current_room.is_position_free(target_x, self.y):
            self.anim_frame = 0
            self.history[0] = (self.history[0][0], self.history[0][1], self.history[0][2], 0)

        if dx != 0 and self.game.current_room.is_position_free(target_x, self.y):
            self.x += dx
            moved = True

        if dy != 0 and self.game.current_room.is_position_free(self.x, target_y):
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

        sx, sy, s_facing, s_frame = self.history[0]
        self.draw(sx, sy, s_facing, s_frame)
            
        self.game.current_room.check_exit(self.x, self.y)
        self.game.current_room.check_trigger(self.x, self.y)


    def draw(self, sx, sy, s_facing, s_frame):
        """Updates the canvas coordinates and images for all party members."""
        # Update Kris
        self.game.canvas.coords(self.active_characters[0], self.x - self.game.camera.x, self.y - self.game.camera.y)
        self.game.canvas.itemconfig(self.active_characters[0], image=self.kris_sprites[self.facing][self.anim_frame])
        
        # Update Susie
        self.game.canvas.coords(self.active_characters[1], sx - self.game.camera.x, sy - self.game.camera.y)
        self.game.canvas.itemconfig(self.active_characters[1], image=self.susie_sprites[s_facing][s_frame])

        if self.y > sy: # Kris is below Susie
            self.game.canvas.tag_raise(self.active_characters[0])
        else:
            self.game.canvas.tag_raise(self.active_characters[1])


    def _move_susie_behind_kris(self, susie_start_coords, kris_facing="down", offset=30):
        """Calculates the target coordinates and begins the cinematic walk loop."""
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
        
        self._susie_walk_step()


    def _susie_walk_step(self):
        """Executes one frame of Susie walking. Moves Y first, then X."""
        reached_y = False
        reached_x = False
        move_facing = "down"
        
        if abs(self._susie_y - self._target_y) > self.speed:
            if self._susie_y < self._target_y:
                self._susie_y += self.speed
                move_facing = "down"
            else:
                self._susie_y -= self.speed
                move_facing = "up"
        else:
            self._susie_y = self._target_y
            reached_y = True
            
        if reached_y:
            if abs(self._susie_x - self._target_x) > self.speed:
                if self._susie_x < self._target_x:
                    self._susie_x += self.speed
                    move_facing = "right"
                else:
                    self._susie_x -= self.speed
                    move_facing = "left"
            else:
                self._susie_x = self._target_x
                reached_x = True
                
        if not (reached_x and reached_y):
            self.game.canvas.coords(
                self.active_characters[1], 
                self._susie_x - self.game.camera.x, 
                self._susie_y - self.game.camera.y
            )
            
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame > 3:
                    self.anim_frame = 0
                    
            self.game.canvas.itemconfig(
                self.active_characters[1], 
                image=self.susie_sprites[move_facing][self.anim_frame]
            )
            
            self.game.root.after(int(1000 / self.game.constants.FPS), self._susie_walk_step)
            
        else:
            self.game.canvas.itemconfig(
                self.active_characters[1],
                image=self.susie_sprites[self.facing][0]
            )
            
            new_history = []
            for i in range(self.follow_delay):
                t = i / (self.follow_delay - 1)
                
                hist_x = self._target_x + (self.x - self._target_x) * t
                hist_y = self._target_y + (self.y - self._target_y) * t
                
                new_history.append((hist_x, hist_y, self.facing, 0))
                
            self.history = new_history