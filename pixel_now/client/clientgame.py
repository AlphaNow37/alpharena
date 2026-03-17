import pygame
pygame.init()

from pixel_now.constants import GRID_SIZE, MAX_ENERGY
from pixel_now.client.tools import get_size
from pixel_now.client.cases_types import Cases, colors
from pixel_now.client.objects import TextOverlay

class PixelNowClient:
    def __init__(self, play_func):
        self.play_func = play_func
        self.screen = pygame.display.set_mode((320, 240), pygame.RESIZABLE)
        pygame.display.set_caption("Client PixelNow")
        self.overlays = []
        self.reset()

    def reset(self):
        self.grid = [[Cases.EMPTY]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.grid_surface = pygame.Surface((GRID_SIZE, GRID_SIZE))
        for x in range(GRID_SIZE):
            self.play_at(x, 0, Cases.OPPONENT)
            self.play_at(x, GRID_SIZE-1, Cases.ME)
        self.energy = 0

    def run(self):
        try:
            self.running = True
            while self.running:
                self.draw()
                pygame.display.flip()
                self.handle_events()
        finally:
            pygame.quit()

    def play_at(self, x, y, player):
        self.grid[y][x] = player
        color = colors.get(player, "purple")
        self.grid_surface.set_at((x, y), color)

    def error(self, message):
        self.overlays.append(TextOverlay(message, "red"))

    def draw(self):
        self.screen.fill("#545454")
        screen_width, screen_height = self.screen.get_size()

        grid_width, grid_height = get_size(screen_width, screen_height, 1, max_y_percent=0.8)
        grid_left = (self.screen.get_width() - grid_width) // 2
        grid_top = (self.screen.get_height() - grid_height) // 2
        surface_grid = pygame.transform.scale(self.grid_surface, (grid_width, grid_height))
        self.screen.blit(surface_grid, (grid_left, grid_top))
        self.last_grid_rect = pygame.Rect(grid_left, grid_top, grid_width, grid_height)

        energy_bar_rect = pygame.Rect(
            grid_left, grid_top+grid_height,
            self.energy/MAX_ENERGY*grid_width, screen_height*0.1
        )
        pygame.draw.rect(self.screen, "yellow", energy_bar_rect)

        x = 0
        while x < len(self.overlays):
            self.overlays[x].draw(self.screen)
            if self.overlays[x].finished:
                self.overlays.pop(x)
            else:
                x += 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if self.last_grid_rect.collidepoint(x, y) and event.button == pygame.BUTTON_LEFT:
                    x = (x - self.last_grid_rect.x) / self.last_grid_rect.width * GRID_SIZE
                    y = (y - self.last_grid_rect.y) / self.last_grid_rect.height * GRID_SIZE
                    self.play_func(int(x), int(y))

    def stop(self):
        self.running = False
