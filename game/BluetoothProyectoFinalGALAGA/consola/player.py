from sprites.sprites import (player_sprite, explode1, explode2,
                             PLAYER_W, PLAYER_H, EXPLODE_W, EXPLODE_H)

class Player:
    def __init__(self, width, height):
        self.x = width // 2 - PLAYER_W // 2
        self.y = height - PLAYER_H
        self.speed = 8
        self.explode_count = 0
        self._width = width
        self._px = self.x
        self._py = self.y

    def move_analog(self, force_x, force_y):
        mov_x = int(force_x * 15)
        mov_y = int(force_y * 15)
        
        if abs(force_y) > 0.15:
            self.x -= mov_y
            if self.x < 0:
                self.x = 0
            if self.x > self._width - PLAYER_W:
                self.x = self._width - PLAYER_W

        if abs(force_x) > 0.15:
            self.y -= mov_x
            if self.y < self._width // 2 - 40: 
                self.y = self._width // 2 - 40
            if self.y > 240 - PLAYER_H:
                self.y = 240 - PLAYER_H

    def draw(self, display):
        display.draw_sprite(player_sprite, self.x, self.y, PLAYER_W, PLAYER_H)
        if self.explode_count:
            explosion = (explode2, explode1)
            display.draw_sprite(explosion[self.explode_count - 1],
                                self.x, self.y, EXPLODE_W, EXPLODE_H)
            self.explode_count -= 1

    def explode(self):
        self.explode_count = 2