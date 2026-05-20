from machine import Pin
import time

class Button:
    UP = 0
    DOWN = 1
    PRESSED = 2
    HELD = 3

    def __init__(self, gpio_num):
        self.pin = Pin(gpio_num, Pin.IN, Pin.PULL_UP)
        self.state = Button.UP
        self.time_pressed = 0

    def _update(self):
        val = self.pin.value()
        now = time.ticks_ms()
        if self.state == Button.UP:
            if val == 0:
                self.time_pressed = now
                self.state = Button.DOWN
        elif self.state == Button.DOWN:
            if val == 1:
                if time.ticks_diff(now, self.time_pressed) > 50:
                    self.state = Button.PRESSED
                else:
                    self.state = Button.UP
            elif time.ticks_diff(now, self.time_pressed) > 200:
                self.state = Button.HELD
        elif self.state == Button.PRESSED:
            self.state = Button.UP
        elif self.state == Button.HELD:
            if val == 1:
                self.state = Button.UP

    def is_pressed(self):
        self._update()
        return self.state == Button.PRESSED

    def is_held(self):
        self._update()
        return self.state == Button.HELD
