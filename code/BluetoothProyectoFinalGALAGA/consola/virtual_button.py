class VirtualButton:
    def __init__(self):
        self._is_pressed = False
        self._was_pressed = False
        self._held_counter = 0

    def update_state(self, is_pressed_bool):
        self._was_pressed = self._is_pressed
        self._is_pressed = is_pressed_bool
        
        if self._is_pressed:
            self._held_counter += 1
        else:
            self._held_counter = 0

    def is_pressed(self):
        pressed_event = self._is_pressed and not self._was_pressed
        if pressed_event:
            self._was_pressed = True 
        return pressed_event

    def is_held(self):
        return self._is_pressed and self._held_counter > 5