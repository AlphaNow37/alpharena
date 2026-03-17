import pygame

from pixel_now.constants import GRID_SIZE
from pixel_now.server.player import Player
from pixel_now.protocol import ActionTypes


class PixelNowServer:
    def __init__(self, senders):
        self.grid: list[list[int | None]] = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]
        for x in range(GRID_SIZE):
            self.grid[0][x] = 1
            self.grid[GRID_SIZE-1][x] = 0
        self.clock = pygame.time.Clock()
        self.players = [Player(i, senders[i]) for i in (0, 1)]
        self.senders = senders

    def play(self, x, y, player):
        for (x_, y_) in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if 0 <= x_ < GRID_SIZE and 0 <= y_ < GRID_SIZE and self.grid[y_][x_] == player:
                self.grid[y][x] = player
                return True
        return False

    def run(self):
        self.running = True
        while self.running:
            self.update()
            self.clock.tick(20)

    def stop(self):
        self.running = False

    def update(self):
        for player in self.players:
            player.energy += 0.1
