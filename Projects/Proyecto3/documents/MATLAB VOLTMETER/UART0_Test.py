####  RUTINA DE PRUEBA PARA EL PUERTO SERIE UART0 QUE
####  SOLO ENVÍA LA PALABRA "HOLA"

from machine import UART, Pin                 # Importa librería la UART.
from time import sleep
machine.freq(270000000)

UART0 = UART(0, baudrate = 460800, tx = Pin(0), rx = Pin(1))   # Para un HC05 460800 bauds

while True:
    UART0.write('HOLA    ')
    sleep(1)