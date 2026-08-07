from abc import ABC, abstractmethod

class Cutscene(ABC):
    @abstractmethod
    def update(self):
        """Method for updating variables & doing calculations each game tick."""
        pass

    @abstractmethod
    def draw(self, surface, camera):
        """Method for drawing the already calculated values on the screen."""
        pass