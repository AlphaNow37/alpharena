from pygame.transform import scale

def get_size(parent_width, parent_height, self_ratio, max_x_percent=1, max_y_percent=1):
    parent_width *= max_x_percent
    parent_height *= max_y_percent
    coef = min(
        parent_width / self_ratio,
        parent_height,
    )
    w = coef * self_ratio
    h = coef
    return w, h

def resize_to(surface, width=None, height=None):
    if width is height is None:
        raise ValueError("width or height must be specified")
    if not (width is None or height is None):
        raise ValueError("width and height cannot be specified at the same time")
    if width is None:
        width = surface.get_width() * height / surface.get_height()
    else:
        height = surface.get_height() * width / surface.get_width()
    return scale(surface, (int(width), int(height)))
