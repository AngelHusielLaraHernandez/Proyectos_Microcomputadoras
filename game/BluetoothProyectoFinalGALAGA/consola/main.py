import uasyncio as asyncio
import aioble
import bluetooth
import struct
from machine import Pin, SPI
from ili9341 import Display
from virtual_button import VirtualButton
from buzzer import Buzzer
from game import Game

_SERVICE_UUID = bluetooth.UUID("12345678-1234-1234-1234-123456789abc")
_CHAR_UUID = bluetooth.UUID("87654321-4321-4321-4321-cba987654321")

SPI_ID   = 0
PIN_SCK  = 18
PIN_MOSI = 19
PIN_MISO = 16
PIN_CS   = 17
PIN_DC   = 20
PIN_RST  = 21
BUZZER_PIN = 15

class ControllerState:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.fire_raw = False
        self.pause_raw = False

ctrl_state = ControllerState()

async def ble_central_task():
    while True:
        try:
            async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
                async for result in scanner:
                    if result.name() == "PicoMando":
                        device = result.device
                        break
                else:
                    continue 

            connection = await device.connect(timeout_ms=2000)
            service = await connection.service(_SERVICE_UUID)
            char = await service.characteristic(_CHAR_UUID)
            await char.subscribe(notify=True)
            
            while True:
                data = await char.notified()
                x, y, fire_val, pause_val = struct.unpack('<ffbb', data)
                
                ctrl_state.x = x
                ctrl_state.y = y
                ctrl_state.fire_raw = bool(fire_val)
                ctrl_state.pause_raw = bool(pause_val)
                
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep_ms(2000)

async def game_task():
    spi = SPI(SPI_ID, baudrate=40_000_000, polarity=0, phase=0,
              sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI), miso=Pin(PIN_MISO))

    display = Display(spi, cs=Pin(PIN_CS, Pin.OUT),
                      dc=Pin(PIN_DC, Pin.OUT),
                      rst=Pin(PIN_RST, Pin.OUT),
                      width=320, height=240, rotation=270)
    display.clear()

    buzz = Buzzer(BUZZER_PIN)
    btn_fire = VirtualButton()
    btn_pause = VirtualButton()

    game = Game(display, buzz, btn_fire, btn_pause, ctrl_state)
    await game.run()

async def main():
    t1 = asyncio.create_task(ble_central_task())
    t2 = asyncio.create_task(game_task())
    await asyncio.gather(t1, t2)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass