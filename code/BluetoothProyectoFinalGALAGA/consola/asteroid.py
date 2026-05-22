import math
from Code.ProyectoFinalGALAGA.sprites.sprites import (fireball, fireball1, guardian1, guardian2,
                             spawn, spawn1, explode1, explode2,
                             FIREBALL_W, FIREBALL_H, GUARDIAN_W, GUARDIAN_H,
                             SPAWN_W, SPAWN_H, EXPLODE_W, EXPLODE_H)

try:
    from urandom import getrandbits, randint
except ImportError:
    from random import getrandbits, randint


class Asteroid:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.dx = 0
        self.active = False
        self.last_spawn = 0
        self._width = width
        self._height = height

    def update(self, frame_count, interval, speed):
        if frame_count - self.last_spawn > interval:
            self.x = randint(0, self._width - FIREBALL_W)
            self.dx = randint(-1, 1)
            self.y = 0
            self.active = True
            self.last_spawn = frame_count
        self.y += speed
        self.x += self.dx
        if self.y > self._height:
            self.active = False

    def draw(self, display, frame_count):
        if self.active:
            sprite = fireball if frame_count & 0x8 else fireball1
            display.draw_sprite(sprite, self.x, self.y, FIREBALL_W, FIREBALL_H)


class Guardian:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.dx = 0
        self.active = False
        self.last_spawn = 0
        self.explode_count = 0
        self._width = width
        self._height = height

    def update(self, frame_count):
        if not self.active and frame_count - self.last_spawn > 50:
            self.x = randint(0, self._width - GUARDIAN_W)
            self.dx = randint(-1, 1)
            self.y = 0
            self.active = True
            self.last_spawn = frame_count
        self.y += 6
        self.x += self.dx
        if self.y > self._height:
            self.active = False

    def draw(self, display, frame_count):
        if self.active:
            sprite = guardian1 if frame_count & 0x8 else guardian2
            display.draw_sprite(sprite, self.x, self.y, GUARDIAN_W, GUARDIAN_H)
        elif self.explode_count:
            explosion = (explode2, explode2, explode1, explode1)
            display.draw_sprite(explosion[self.explode_count - 1],
                                self.x, self.y, EXPLODE_W, EXPLODE_H)
            self.explode_count -= 1

    def explode(self):
        self.explode_count = 4


class DiveBomber:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.active = False
        self.last_spawn = 0
        self.explode_count = 0
        self._width = width
        self._height = height

    def update(self, frame_count, interval, speed, enemies):
        if not self.active and frame_count - self.last_spawn > interval:
            row2 = [e for e in enemies if e.alive and e.row == 2]
            if row2:
                e = row2[randint(0, len(row2) - 1)]
                self.x = e.x
                self.y = e.y
                self.active = True
                self.last_spawn = frame_count
        self.y += speed
        self.x = self._width // 2 + int(20 * math.sin(3 * 2 * math.pi * self.y / self._height))
        if self.y > self._height:
            self.active = False

    def draw(self, display, frame_count):
        if self.active:
            sprite = spawn if frame_count & 0x8 else spawn1
            display.draw_sprite(sprite, self.x, self.y, SPAWN_W, SPAWN_H)
        elif self.explode_count:
            explosion = (explode2, explode2, explode1, explode1)
            display.draw_sprite(explosion[self.explode_count - 1],
                                self.x, self.y, EXPLODE_W, EXPLODE_H)
            self.explode_count -= 1

    def explode(self):
        self.explode_count = 4
