import pygame
from pixel_now.client.tools import get_size
import time


class TextOverlay:
    font = pygame.font.SysFont("comicsansms", 20)

    def __init__(self, text, color="red"):
        self.textsurface = self.font.render(text, True, color)
        self.ratio = self.textsurface.get_width() / self.textsurface.get_height()
        self.creating_time = time.time()
        self.finished = False

    def draw(self, screen):
        act_time = time.time()
        delta = act_time - self.creating_time
        self.textsurface.set_alpha(int(255*(1-delta)))

        sc_width, sc_height = screen.get_size()
        width, height = get_size(sc_width, sc_height, self.ratio, 0.5, 0.1)
        x = (sc_width - width) // 2
        y = (sc_height - height) // 2 + (delta * sc_height//10)
        resized = pygame.transform.scale(self.textsurface, (width, height))
        screen.blit(resized, (x, y))
        self.finished = delta >= 1
