from machine import Pin
import time

BTN_LEFT  = 2
BTN_RIGHT = 3
BTN_FIRE  = 4
BTN_PAUSE = 5

pins = {
    'LEFT (GP2)':  Pin(BTN_LEFT,  Pin.IN, Pin.PULL_UP),
    'RIGHT (GP3)': Pin(BTN_RIGHT, Pin.IN, Pin.PULL_UP),
    'FIRE (GP4)':  Pin(BTN_FIRE,  Pin.IN, Pin.PULL_UP),
    'PAUSE (GP5)': Pin(BTN_PAUSE, Pin.IN, Pin.PULL_UP),
}

print("=== TEST DE BOTONES ===")
print("Con PULL_UP: 1 = no presionado, 0 = presionado")
print("Presiona cada boton para verificar...")
print("Ctrl+C para salir")
print()

while True:
    line = ""
    for name, pin in pins.items():
        val = pin.value()
        estado = "PRESIONADO" if val == 0 else "---"
        line += "{}: {} ({})  ".format(name, val, estado)
    print(line)
    time.sleep_ms(200)
