import pathlib
import json
import pygame

SET = (255, 255, 255)
UNSET = (0, 0, 0)
SIZE_MULTIPLIER = 8

maps_path = pathlib.Path(__file__).parent / 'maps'
raw_maps = {
    map_file.name.removesuffix(".json"):
        json.loads(map_file.read_text("utf-8"))
    for map_file in maps_path.iterdir()
}
class Map:
    def __init__(self, name):
        self.raw = raw_maps[name]
        self.mask = _get_mask(self.raw)
        self.size = self.raw["radius"] * 2
        self.starting_pos = self.raw["starting_positions"]
        self._hash = hash(name)
        self.multiplier = SIZE_MULTIPLIER

    def __hash__(self):
        return self._hash

    def do_collide(self, x, y):
        x *= SIZE_MULTIPLIER
        y *= SIZE_MULTIPLIER
        return bool(self.mask.overlap(self.player_mask, (x, y)))

    @property
    def surface(self):
        if hasattr(self, "_surface"):
            return self._surface
        self._surface = self.mask.to_surface(setcolor="#333333", unsetcolor="#AAAAAA")
        return self._surface

    @property
    def player_mask(self):
        if hasattr(self, "_player_mask"):
            return self._player_mask
        circle = pygame.Surface((SIZE_MULTIPLIER, SIZE_MULTIPLIER))
        pygame.draw.circle(circle, (1, 1, 1), (SIZE_MULTIPLIER // 2, SIZE_MULTIPLIER // 2), SIZE_MULTIPLIER // 2)
        circle.set_colorkey((0, 0, 0))
        self._player_mask = pygame.mask.from_surface(circle)
        return self._player_mask

    def get_line_steps(self, from_: pygame.Vector2, delta: pygame.Vector2, lenght=None):
        from_ = from_ * SIZE_MULTIPLIER
        delta = delta * SIZE_MULTIPLIER
        if not delta:
            return
        if lenght is None:
            n_steps = float("inf")
        else:
            n_steps = int(lenght * SIZE_MULTIPLIER)
        delta.scale_to_length(1)
        max_x, max_y = self.mask.get_size()
        step_i = 0
        while step_i < n_steps:
            x, y = from_ + delta * step_i
            if x < 0 or x >= max_x or y < 0 or y >= max_y:
                break
            if self.mask.get_at((x, y)):
                return
            step_i += 1
            yield pygame.Vector2(x, y)

def _get_mask(raw) -> pygame.mask.Mask:
    radius = raw["radius"] * SIZE_MULTIPLIER
    surface = pygame.Surface((radius * 2, radius * 2))
    surface.fill(SET)
    pygame.draw.circle(surface, UNSET, (radius, radius), radius)
    for points in raw["lines"]:
        points = [[coo * SIZE_MULTIPLIER for coo in point] for point in points]
        pygame.draw.line(surface, SET, *points, width=SIZE_MULTIPLIER)
    surface.set_colorkey(UNSET)
    return pygame.mask.from_surface(surface)
