from abc import ABC, abstractmethod

class Cutscene(ABC):
    def __init__(self):
        self.action_queue = []
        self._current_action_started = False

    def update(self):
        """Processes the action queue each game tick."""
        if not self.action_queue: return

        current_action = self.action_queue[0]

        if not self._current_action_started:
            current_action.start()
            self._current_action_started = True

        is_finished = current_action.update()
        if is_finished:
            self.action_queue.pop(0)
            self._current_action_started = False
        

    @abstractmethod
    def draw(self, surface, camera):
        """Abstract method for drawing the already calculated values on the screen."""
        pass