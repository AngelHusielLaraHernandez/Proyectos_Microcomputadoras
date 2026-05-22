from machine import Pin, SPI, I2C
import time

from ili9341 import Display
from Code.ProyectoFinalGALAGA.button import Button
from Code.ProyectoFinalGALAGA.buzzer import Buzzer
from Code.ProyectoFinalGALAGA.game import Game
from imu import MPU6050


SPI_ID   = 0
PIN_SCK  = 18
PIN_MOSI = 19
PIN_MISO = 16
PIN_CS   = 17
PIN_DC   = 20
PIN_RST  = 21


BTN_FIRE  = 4
BTN_PAUSE = 5
BUZZER_PIN = 15

spi = SPI(SPI_ID, baudrate=40_000_000, polarity=0, phase=0,
          sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI), miso=Pin(PIN_MISO))

display = Display(spi, cs=Pin(PIN_CS, Pin.OUT),
                  dc=Pin(PIN_DC, Pin.OUT),
                  rst=Pin(PIN_RST, Pin.OUT),
                  width=320, height=240, rotation=270)
display.clear()

i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000)
imu = MPU6050(i2c)


btn_fire  = Button(BTN_FIRE)
btn_pause = Button(BTN_PAUSE)
buzz      = Buzzer(BUZZER_PIN)


game = Game(display, buzz, btn_fire, btn_pause, imu)
game.run()
