from machine import Pin, ADC, UART, PWM
from time import sleep_ms, sleep_us, ticks_us, ticks_diff
import _thread
import struct

ADC0 = ADC(Pin(26))
UART0 = UART(0, baudrate=460800, tx=Pin(0), rx=Pin(1))

Pin3 = PWM(Pin(3))
Pin3.freq(50)
Pin3.duty_u16(32768)

conversion_factor = 3.3 / 65535
MUESTRAS = 1000
ENTRADAS = [0.0] * MUESTRAS
SALIDAS = [0.0] * MUESTRAS

CTE_A0 = 0.0303
CTE_A1 = 0.0303
CTE_A2 = 0.0
CTE_B1 = 0.9394
CTE_B2 = 0.0
FREQ = 50.0
nueva_freq = False

def hilo_generador():
    global nueva_freq
    freq_actual = 50
    while True:
        if nueva_freq:
            f = FREQ
            if f >= 1:
                Pin3.freq(int(f))
                Pin3.duty_u16(32768)
                freq_actual = f
            nueva_freq = False
        sleep_ms(10)

_thread.start_new_thread(hilo_generador, ())

while True:
    if UART0.any() > 0:
        sleep_ms(100)
        LLAVE = UART0.read()

        if LLAVE is None:
            continue

        if len(LLAVE) >= 25 and LLAVE[0] == 0x55:
            CTE_A0 = struct.unpack('<f', LLAVE[1:5])[0]
            CTE_A1 = struct.unpack('<f', LLAVE[5:9])[0]
            CTE_A2 = struct.unpack('<f', LLAVE[9:13])[0]
            CTE_B1 = struct.unpack('<f', LLAVE[13:17])[0]
            CTE_B2 = struct.unpack('<f', LLAVE[17:21])[0]
            FREQ = struct.unpack('<f', LLAVE[21:25])[0]
            nueva_freq = True

            print("Coeficientes recibidos:")
            print("  A0 = {}".format(CTE_A0))
            print("  A1 = {}".format(CTE_A1))
            print("  A2 = {}".format(CTE_A2))
            print("  B1 = {}".format(CTE_B1))
            print("  B2 = {}".format(CTE_B2))
            print("  FREQ = {} Hz".format(FREQ))

        if 0x52 in LLAVE:
            a0 = CTE_A0
            a1 = CTE_A1
            a2 = CTE_A2
            b1 = CTE_B1
            b2 = CTE_B2

            uk = 0.0
            uk1 = 0.0
            uk2 = 0.0
            yk = 0.0
            yk1 = 0.0
            yk2 = 0.0

            for i in range(500):
                t_inicio = ticks_us()

                yk = a0 * uk + a1 * uk1 + a2 * uk2 + b1 * yk1 + b2 * yk2

                uk2 = uk1
                uk1 = uk
                yk2 = yk1
                yk1 = yk

                uk = ADC0.read_u16() * conversion_factor
                ENTRADAS[i] = uk
                SALIDAS[i] = yk

                while ticks_diff(ticks_us(), t_inicio) < 125:
                    pass

            En_Bytes = bytearray(struct.pack('f', ENTRADAS[0]))
            En_Bytes += bytearray(struct.pack('f', SALIDAS[0]))
            for k in range(1, 500):
                En_Bytes += bytearray(struct.pack('f', ENTRADAS[k]))
                En_Bytes += bytearray(struct.pack('f', SALIDAS[k]))

            for j in range(0, len(En_Bytes), 50):
                UART0.write(En_Bytes[j:j + 50])
                sleep_ms(60)

            En_Bytes = bytearray()

