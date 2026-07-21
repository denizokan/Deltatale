from PIL import Image, ImageTk

class TransitionManager:
    """Handles smooth screen fade transitions."""
    def __init__(self, main_game):
        self.game = main_game
        self.fade_alpha = 0
        self.fade_canvas_image = None
        self.fade_image_ref = None
        self.is_transitioning = False

    def fade_to_black(self, speed=8, on_complete=None):
        """Fades the screen out, then runs the on_complete function."""
        if self.is_transitioning: return
        self.is_transitioning = True
        self.fade_alpha = 0
        self._animate(speed, 255, on_complete)

    def fade_from_black(self, speed=8, on_complete=None):
        """Reveals the screen, then runs the on_complete function."""
        if self.is_transitioning: return
        self.is_transitioning = True
        self.fade_alpha = 255
        self._animate(-speed, 0, on_complete)

    def _animate(self, speed, target_alpha, on_complete):
        """The internal loop that updates the image opacity."""
        self.fade_alpha += speed

        if self.fade_alpha >= 255: self.fade_alpha = 255
        if self.fade_alpha <= 0: self.fade_alpha = 0

        img = Image.new('RGBA', (self.game.constants.WIDTH, self.game.constants.HEIGHT), (0, 0, 0, self.fade_alpha))
        self.fade_image_ref = ImageTk.PhotoImage(img)

        if self.fade_canvas_image is None:
            self.fade_canvas_image = self.game.canvas.create_image(0, 0, image=self.fade_image_ref, anchor="nw")
        else:
            self.game.canvas.itemconfig(self.fade_canvas_image, image=self.fade_image_ref)

        self.game.canvas.tag_raise(self.fade_canvas_image)

        if self.fade_alpha == target_alpha:
            self.is_transitioning = False
            if self.fade_alpha == 0 and self.fade_canvas_image:
                self.game.canvas.delete(self.fade_canvas_image)
                self.fade_canvas_image = None
                self.fade_image_ref = None
                
            if on_complete:
                on_complete()
        else:
            delay = int(1000 / self.game.constants.FPS)
            self.game.root.after(delay, lambda: self._animate(speed, target_alpha, on_complete))