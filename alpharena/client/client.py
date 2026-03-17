import socket
import pygame
import time
from functools import cache


pygame.init()

from alpharena.protocol import Sender, Recever, ActionTypes
from alpharena.client.overlays import Overlay, TextOverlay
from alpharena.map import Map
from alpharena.constants import FOG_DISTANCE

class Client:
    font = pygame.font.SysFont("monospace", 12)

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((socket.gethostname(), 8080))
        print("Client in port ", self.sock.getsockname())
        self.recever = Recever(self.sock)
        self.event_queue = self.recever.events
        self.sender = Sender(self.sock)

        self.screen = pygame.display.set_mode((320, 240), pygame.RESIZABLE)
        pygame.display.set_caption("alpharena Client")

        self.last_move_request = 0

        self.running = True
        self.send_stop_message = True
        self.projectiles: dict[int, pygame.Vector2] = {}
        try:
            self.reset()
            self.run()
        finally:
            if self.send_stop_message:
                self.sender.send(ActionTypes.STOP_GAME)
            self.recever.running = False
            pygame.quit()
            time.sleep(0.5)
            self.recever.close()
            self.sock.close()
            print("Client closed")

    def run(self):
        self._last_frame_time = time.time()
        self.last_fps = [float("inf")]*15
        while self.running:
            act_time = time.time()
            delta = act_time - self._last_frame_time
            if delta == 0:
                fps = float("inf")
            else:
                fps = 1/(act_time - self._last_frame_time)
            self.last_fps.pop(0)
            self.last_fps.append(fps)
            self.fps = sum(self.last_fps)/len(self.last_fps)
            self._last_frame_time = act_time

            self.draw()
            pygame.display.flip()
            self.events()

    def events(self):
        for action_type, args in self.event_queue:
            print(f"[Event] {action_type}{args}")
            if action_type is ActionTypes.STOP_GAME:
                self.send_stop_message = False
                self.running = False
            elif action_type is ActionTypes.ERROR:
                self.overlays.append(TextOverlay(args[0], "red"))
            elif action_type is ActionTypes.MOVE_TO:
                self.pos[:] = args
                self.pos /= 128
            elif action_type is ActionTypes.OPP_MOVE_TO:
                self.opp_pos[:] = args
                self.opp_pos /= 128
            elif action_type is ActionTypes.NEW_PROJECTILE:
                self.projectiles[args[0]] = pygame.Vector2(0, 0)
            elif action_type is ActionTypes.PROJECTILE_MOVE_TO:
                self.projectiles[args[0]][:] = args[1:]
                self.projectiles[args[0]] /= 128
            elif action_type is ActionTypes.PROJECTILE_DESTROYED:
                del self.projectiles[args[0]]
            elif action_type is ActionTypes.SET_LIFE:
                self.life = args[0]
            elif action_type is ActionTypes.SET_OPP_LIFE:
                self.opp_life = args[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if self.map_rect.collidepoint(event.pos):
                        mouse_pos = pygame.Vector2(event.pos)
                        mouse_pos.x -= self.map_rect.x
                        mouse_pos.y -= self.map_rect.y
                        mouse_pos = mouse_pos / self.map_rect.width * self.map.size
                        mouse_pos -= self.pos
                        self.sender.send(ActionTypes.SHOOT, list(map(int, mouse_pos*128)))

        act_time = time.time()
        if act_time - self.last_move_request > 0.05:
            pressed = pygame.key.get_pressed()
            x, y = self.pos
            x_inc = 0
            y_inc = 0
            if pressed[pygame.K_z]:
                y_inc = -1
            if pressed[pygame.K_s]:
                y_inc = 1
            if pressed[pygame.K_q]:
                x_inc = -1
            if pressed[pygame.K_d]:
                x_inc = 1
            new_pos = pygame.Vector2(self.pos)
            for _ in range(10):
                x += x_inc/10
                y += y_inc/10
                x = max(0, min(x, self.map.size - 1))
                y = max(0, min(y, self.map.size - 1))
                if self.map.do_collide(x, y):
                    break
                else:
                    new_pos.x = x
                    new_pos.y = y
            if new_pos != self.pos:
                self.pos = new_pos
                self.sender.send(ActionTypes.MOVE_TO, (int(self.pos.x*128), int(self.pos.y*128)))
                self.last_move_request = act_time

    def draw(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill("#545454")

        map_surface = self.map.surface.copy()

        black_overlay = get_black_overlay(self.map, (self.pos.x + 0.5, self.pos.y + 0.5))
        map_surface.blit(black_overlay, (0, 0))

        player_pos = tuple(map(int, (self.pos+(0.5, 0.5)) * self.map.multiplier))
        pygame.draw.circle(map_surface, "blue", player_pos, self.map.multiplier // 2)

        if self.pos.distance_to(self.opp_pos) < FOG_DISTANCE:
            opp_pos = tuple(map(int, self.opp_pos * self.map.multiplier))
            pygame.draw.circle(map_surface, "red", opp_pos, self.map.multiplier // 2)

        for proj in self.projectiles.values():
            proj_pos = tuple(map(int, proj * self.map.multiplier))
            pygame.draw.circle(map_surface, "green", proj_pos, self.map.multiplier // 2)

        map_size = min(screen_width, screen_height)

        if map_size < 0.9 * screen_width:
            life_on_left = True
        elif map_size < 0.9 * screen_height:
            life_on_left = False
        else:
            map_size = 0.9 * max(screen_width, screen_height)
            life_on_left = screen_width > screen_height

        map_x = (screen_width - map_size) // 2
        map_y = (screen_height - map_size) // 2
        map_surface = pygame.transform.scale(map_surface, (map_size, map_size))
        self.screen.blit(map_surface, (map_x, map_y))
        self.map_rect = pygame.Rect(map_x, map_y, map_size, map_size)

        if life_on_left:
            myrect = pygame.Rect(map_x-screen_width*0.05, 0, screen_width*0.05, screen_height * self.life/100)
            opp_rect = pygame.Rect(map_x+map_size, 0, screen_width*0.05, screen_height * self.opp_life/100)
        else:
            myrect = pygame.Rect(0, map_y-screen_height*0.1, screen_width * self.life/100, screen_height*0.05)
            opp_rect = pygame.Rect(0, map_y+map_size, screen_width * self.opp_life/100, screen_height*0.05)
        pygame.draw.rect(self.screen, "blue", myrect)
        pygame.draw.rect(self.screen, "red", opp_rect)

        for overlay in self.overlays:
            overlay.draw(self.screen)

        self.screen.blit(self.font.render(f"FPS: {self.fps:.2f}", True, "white"), (0, 0))

    def reset(self):
        self.map = Map("map")
        self.overlays: list[Overlay] = []
        self.pos = pygame.Vector2(0, 0)
        self.opp_pos = pygame.Vector2(0, 0)

        self.life = 100
        self.opp_life = 100

    def __hash__(self):  # For @cache
        return 0

@cache
def get_black_overlay(map_: Map, act_pos):
    act_pos = pygame.Vector2(act_pos)
    surface = pygame.Surface(map_.mask.get_size())
    surface.fill("#000000")
    vec = pygame.math.Vector2(FOG_DISTANCE, 0)
    for angle in range(360):
        o_vec = vec.rotate(angle)
        for x, y in map_.get_line_steps(act_pos, o_vec, lenght=FOG_DISTANCE):
            surface.set_at((int(x), int(y)), (1, 1, 1))
    surface.set_alpha(128)
    surface.set_colorkey((1, 1, 1))
    return surface
