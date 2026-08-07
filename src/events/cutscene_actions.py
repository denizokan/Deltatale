from abc import ABC, abstractmethod
import pygame

class CutsceneAction(ABC):
    @abstractmethod
    def start(self):
        """Called once when the action reaches the front of the queue."""
        pass

    @abstractmethod
    def update(self) -> bool:
        """Called every game tick. Returns True when the action is completely finished."""
        pass


class ParallelAction(CutsceneAction):
    """Runs multiple actions at once and waits until all are done."""
    def __init__(self, *actions):
        self.actions = list(actions)
        self.finished = [False] * len(self.actions)

    def start(self):
        for action in self.actions:
            action.start()

    def update(self):
        all_done = True
        for i, action in enumerate(self.actions):
            if not self.finished[i]:
                if action.update():
                    self.finished[i] = True
                else:
                    all_done = False
        return all_done


class CutsceneSequence(CutsceneAction):
    """Executes a list of actions sequentially. Useful for nesting inside a ParallelAction."""
    def __init__(self, actions):
        self.actions = list(actions)
        self.current_index = 0
        self._action_started = False

    def start(self):
        self.current_index = 0
        self._action_started = False

    def update(self):
        while self.current_index < len(self.actions):
            current_action = self.actions[self.current_index]

            if not self._action_started:
                current_action.start()
                self._action_started = True

            is_finished = current_action.update()

            if is_finished:
                self.current_index += 1
                self._action_started = False
            else:
                return False 

        return True


class WaitAction(CutsceneAction):
    """Waits for the given ms amount of time."""
    def __init__(self, duration_ms):
        self.duration_ms = duration_ms
        self.start_time = 0

    def start(self):
        self.start_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        return (now - self.start_time) >= self.duration_ms


class DialogueAction(CutsceneAction):
    """Stars a dialogue and waits until it's over."""
    def __init__(self, context, dialogue_data, actors=None, is_battle=False):
        self.context = context
        self.dialogue_data = dialogue_data
        self.actors = actors
        self.is_battle = is_battle
        self.is_done = False

    def start(self):
        self.context.dialogue.start_dialogue(
            self.dialogue_data,
            on_complete=self.on_dialogue_complete,
            actors=self.actors,
            is_battle=self.is_battle
        )

    def on_dialogue_complete(self):
        self.is_done = True

    def update(self):
        return self.is_done


class PlaySoundAction(CutsceneAction):
    """Plays a sound and ends."""
    def __init__(self, sound, loops=0):
        self.sound = sound
        self.loops = loops

    def start(self):
        self.sound.play(loops=self.loops)

    def update(self):
        return True


class AnimateAction(CutsceneAction):
    """Starts an animation and waits until it finishes."""
    def __init__(self, target_obj, attribute_name, frames, delay_ms):
        self.target = target_obj
        self.attribute_name = attribute_name
        self.frames = frames
        self.delay_ms = delay_ms
        self.current_index = 0
        self.last_update = 0

    def start(self):
        self.last_update = pygame.time.get_ticks()
        setattr(self.target, self.attribute_name, self.frames[0])

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.delay_ms:
            self.current_index += 1

            if self.current_index >= len(self.frames):
                return True

            setattr(self.target, self.attribute_name, self.frames[self.current_index])
            self.last_update = now

        return False


class CallAction(CutsceneAction):
    """Instantly calls an action and finishes."""
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def start(self):
        self.func(*self.args, **self.kwargs)

    def update(self):
        return True


class CustomLoopAction(CutsceneAction):
    """
    Runs an update function every frame. 
    If check_done_func is provided, it returns the result of that function.
    Otherwise, it returns whatever the update_func itself returns.
    """
    def __init__(self, update_func, check_done_func=None):
        self.update_func = update_func
        self.check_done_func = check_done_func

    def start(self):
        pass

    def update(self):
        result = self.update_func()
        
        if self.check_done_func:
            return self.check_done_func()
            
        return bool(result)


class SlideAction(CutsceneAction):
    """Moves an object or dictionary from point A to point B smoothly."""
    def __init__(self, obj, attr_x, attr_y, end_pos, duration_ms, ease_out=True):
        self.obj = obj
        self.attr_x = attr_x
        self.attr_y = attr_y
        self.end_pos = end_pos
        self.duration_ms = max(1, duration_ms)
        self.ease_out = ease_out

    def start(self):
        self.start_time = pygame.time.get_ticks()
        
        if isinstance(self.obj, dict):
            self.start_pos = (self.obj[self.attr_x], self.obj[self.attr_y])
        else:
            self.start_pos = (getattr(self.obj, self.attr_x), getattr(self.obj, self.attr_y))

    def update(self):
        now = pygame.time.get_ticks()
        t = (now - self.start_time) / self.duration_ms
        
        if t >= 1.0:
            self._set_val(self.attr_x, self.end_pos[0])
            self._set_val(self.attr_y, self.end_pos[1])
            return True

        ease_t = 1 - (1 - t)**3 if self.ease_out else t
        new_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * ease_t
        new_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * ease_t
        
        self._set_val(self.attr_x, new_x)
        self._set_val(self.attr_y, new_y)
        return False

    def _set_val(self, key, value):
        if isinstance(self.obj, dict):
            self.obj[key] = value
        else:
            setattr(self.obj, key, value)