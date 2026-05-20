from Code.ProyectoFinalGALAGA.sprites.sprites import (alien1, alien2, alien3, alien4, alien5, alien6,
                             explode1, explode2, ALIEN_W, ALIEN_H,
                             EXPLODE_W, EXPLODE_H)

_ALIEN_PAIRS = ((alien1, alien2), (alien3, alien4), (alien5, alien6))
_SCORES = (30, 20, 10)

class Enemy:
    def __init__(self, start_x, start_y, row):
        self.x = start_x
        self.y = start_y
        self.alive = True
        self.row = row
        self.score = _SCORES[row % 3]
        self.explode_count = 0

    def draw(self, display, frame_count):
        if self.alive:
            pair = _ALIEN_PAIRS[self.row % 3]
            sprite = pair[0] if frame_count & 0x8 else pair[1]
            display.draw_sprite(sprite, self.x, self.y, ALIEN_W, ALIEN_H)
        elif self.explode_count:
            explosion = (explode2, explode2, explode1, explode1)
            display.draw_sprite(explosion[self.explode_count - 1],
                                self.x, self.y, EXPLODE_W, EXPLODE_H)
            self.explode_count -= 1

    def explode(self):
        self.explode_count = 4
