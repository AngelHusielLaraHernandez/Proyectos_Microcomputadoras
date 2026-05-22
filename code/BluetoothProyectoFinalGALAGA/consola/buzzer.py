from machine import Pin, PWM
import time

class Buzzer:
    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.pwm = None
        self._queue = []
        self._current = None
        self._start_time = 0

    def _start_pwm(self, freq):
        if self.pwm is not None:
            self.pwm.deinit()
        if freq > 0:
            self.pwm = PWM(Pin(self.pin_num))
            self.pwm.freq(freq)
            self.pwm.duty_u16(512)
        else:
            self.pwm = None

    def _stop_pwm(self):
        if self.pwm is not None:
            self.pwm.duty_u16(0)
            self.pwm.deinit()
            self.pwm = None

    def tone(self, freq, duration_ms):
        self._queue.append((freq, duration_ms))

    def noise(self, duration_ms):
        self._queue.append((200, min(duration_ms, 50)))

    def play_shoot(self):
        self.tone(1000, 30)
        self.tone(400, 30)

    def play_explosion(self):
        self.tone(100, 40)
        self.tone(80, 40)
        self.tone(60, 40)

    def play_enemy_shoot(self):
        self.tone(200, 20)
        self.tone(150, 20)

    def play_hit(self):
        self.tone(110, 30)
        self.noise(50)

    def play_powerup(self):
        self.tone(800, 50)
        self.tone(1200, 50)
        self.tone(2000, 80)

    def play_killed(self):
        for f in [1046, 988, 880, 784, 698, 659, 587]:
            self.tone(f, 80)

    def play_next_level(self):
        for f in [523, 659, 784, 1046, 1319, 1568]:
            self.tone(f, 60)

    def play_start(self):
        for f in [1046, 1319, 1568, 2093, 1568, 1319, 1046]:
            self.tone(f, 60)

    def play_menu_note(self, idx):
        notes = [659, 784, 659, 523, 659, 784, 659, 880,
                 1047, 1319, 1047, 880, 1047, 1319, 1047]
        f = notes[idx % len(notes)]
        self.tone(f, 80)

    def update(self):
        now = time.ticks_ms()
        if self._current is not None:
            freq, dur = self._current
            if time.ticks_diff(now, self._start_time) >= dur:
                self._stop_pwm()
                self._current = None
            return

        if self._queue:
            self._current = self._queue.pop(0)
            freq, dur = self._current
            self._start_time = now
            if freq > 0:
                self._start_pwm(freq)
            return

    def stop(self):
        self._queue.clear()
        self._current = None
        self._stop_pwm()
