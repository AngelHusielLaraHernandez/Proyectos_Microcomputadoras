class Bullet:
    def __init__(self, x, y, dy, color, height):
        self.x = x
        self.y = y
        self.dy = dy
        self.active = True
        self.color = color
        self._height = height

    def update(self):
        self.y += self.dy
        if self.y < 0 or self.y > self._height:
            self.active = False

    def draw(self, display):
        if self.active:
            display.fill_hrect(self.x, self.y, 2, 4, self.color)
