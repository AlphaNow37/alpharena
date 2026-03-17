import pygame
import time

from alpharena.client.tools import get_size

class Overlay:
    max_w_percent: float = 1
    max_h_percent: float = 1
    life_maxtime: float = float("inf")

    def __init__(self, image):
        super().__init__()
        self.image = image
        self._ratio = self.image.get_width() / self.image.get_height()
        self.created_time = time.time()
        self.finished = False

    def draw(self, screen):
        time_delta = time.time() - self.created_time
        life_percent = time_delta / self.life_maxtime
        if life_percent > 1:
            self.finished = True
            return
        screen_w, screen_h = screen.get_size()
        width, height = get_size(screen_w, screen_h, self._ratio, self.max_w_percent, self.max_h_percent)
        self_surface = pygame.transform.scale(self.image, (width, height))
        self_surface.set_alpha(int(255 * (1-life_percent)))
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2 + screen_h/10*life_percent
        screen.blit(self_surface, (x, y))

class TextOverlay(Overlay):
    _font = pygame.font.SysFont("Arial", 20)
    max_w_percent = 0.5
    max_h_percent = 0.1
    life_maxtime = 1

    def __init__(self, text, color):
        surface = self._font.render(text, True, color)
        super().__init__(surface)
