import pygame
import time

from alpharena.protocol import ActionTypes
from alpharena.map import Map
from alpharena.constants import SHOOTING_TIME

ID = 0

class Entity:
    __position: pygame.math.Vector2 = pygame.math.Vector2(0, 0)

    x = property(lambda self: self.__position.x, lambda self, value: self.position.__setitem__(0, value))
    y = property(lambda self: self.__position.y, lambda self, value: self.position.__setitem__(1, value))

    def update_pos(self, x, y):
        raise NotImplementedError

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = pygame.math.Vector2(value)
        self.update_pos(*self.pos_to_int())

    def pos_to_int(self):
        return int(self.__position.x * 128), int(self.__position.y * 128)


class Player(Entity):
    __life = 0

    def __init__(self, i, sender, opp_sender, map_: Map, position, projectiles, reset_func):
        self._i = i
        self._sender = sender
        self._opp_sender = opp_sender
        self._map = map_
        self.position = position
        self._next_shoot_time = 0
        self._projectiles = projectiles
        self.life = 100
        self._reset_func = reset_func

        self.opponent = None  # Change later in server.py

    def update_pos(self, x, y):
        self._sender.send(ActionTypes.MOVE_TO, (x, y))
        self._opp_sender.send(ActionTypes.OPP_MOVE_TO, (x, y))

    def move_to(self, x, y) -> bool:
        if (not 0 <= x < self._map.size) or (not 0 <= y < self._map.size):
            return False
        if not self._map.do_collide(x, y):
            self.position = (x, y)
            return True
        return False

    def shoot(self, x, y) -> bool:
        act_time = time.time()
        if self._next_shoot_time > act_time:
            return False
        self._next_shoot_time = act_time + SHOOTING_TIME
        vec = pygame.math.Vector2(x, y)
        proj = Projectile(self.opponent, (self._sender, self._opp_sender), self._map, self.position+(0.5, 0.5), vec)
        self._projectiles[proj.id] = proj
        return True

    @property
    def life(self):
        return self.__life

    @life.setter
    def life(self, value):
        value = min(100, value)
        if value < 0:
            print("Game Over")
            self._sender.send(ActionTypes.ERROR, "you lose !")
            self._opp_sender.send(ActionTypes.ERROR, "you win !")
            self._sender.send(ActionTypes.RESET)
            self._opp_sender.send(ActionTypes.RESET)
            self._reset_func()
            return
        if int(value/5) != int(self.__life/5):
            self._sender.send(ActionTypes.SET_LIFE, (int(value),))
            self._opp_sender.send(ActionTypes.SET_OPP_LIFE, (int(value),))
        self.__life = value


class Projectile(Entity):
    def __init__(self, opponent, senders, map_: Map, position, vec):
        global ID
        self.id = ID
        ID += 1

        self._last_position_update = 0
        self.finished = False

        for sender in senders:
            sender.send(ActionTypes.NEW_PROJECTILE, self.id)

        self._senders = senders
        self.position = position
        self._dir_vec = vec
        self._opponent = opponent
        self._map = map_
        self._mover = self.move()

    def move(self):
        for pos in self._map.get_line_steps(self.position, self._dir_vec):
            self.position = pos / self._map.multiplier
            if self.position.distance_to(self._opponent.position) < 1:
                self._opponent.life -= 20
                return
            yield

    def destroy(self):
        self.finished = True
        for sender in self._senders:
            sender.send(ActionTypes.PROJECTILE_DESTROYED, self.id)

    def update(self):
        try:
            for _ in range(5):
                next(self._mover)
        except StopIteration:
            self.finished = True

    def update_pos(self, x, y):
        if self.finished:
            return
        act_time = time.time()
        if act_time - self._last_position_update > 1/10:
            for sender in self._senders:
                sender.send(ActionTypes.PROJECTILE_MOVE_TO, (self.id, x, y))
            self._last_position_update = act_time
