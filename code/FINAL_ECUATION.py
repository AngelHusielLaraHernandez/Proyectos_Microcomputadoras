import machine
try:
    machine.freq(300_000_000)
except:
    print("CPU:", machine.freq(), "Hz")
    pass
#print("CPU:", machine.freq(), "Hz")

from machine import Pin, ADC, UART
from time import sleep, sleep_ms, sleep_us, ticks_us, ticks_diff, ticks_add
import _thread
import struct

# Limpiar cualquier PWM residual en Pin 3 de ejecuciones anteriores
try:
    from machine import PWM
    _p = PWM(Pin(3))
    _p.deinit()
except:
    pass

ADC0 = ADC(Pin(26))
Pin3 = Pin(3, Pin.OUT)

UART0 = UART(0, baudrate=460800, tx=Pin(0), rx=Pin(1))

conversion_factor = 3.3 / (65535)
MUESTRAS = 1000
ENTRADAS = [0]*MUESTRAS
SALIDAS  = [0]*MUESTRAS
En_Bytes = bytearray(4000)

To_CTE_A0 = bytearray(4)
To_CTE_A1 = bytearray(4)
To_CTE_A2 = bytearray(4)
To_CTE_B1 = bytearray(4)
To_CTE_B2 = bytearray(4)
To_FREQ   = bytearray(4)

CTE_A0 = +0.0303
CTE_A1 = +0.0303
CTE_A2 = +0.0
CTE_B1 = +0.9394
CTE_B2 = +0.0
FREQ    = 50
PERIODO = (1/FREQ)
HALF    = int((PERIODO*1000000)/2)

UK, UK1, UK2 = 0.0, 0.0, 0.0
YK, YK1, YK2 = 0.0, 0.0, 0.0
Read = 0.0

# ---------------------------------------------------------
# HILO: Onda cuadrada pura con toggle manual (Pin3)
# ---------------------------------------------------------
def Onda_Cuadrada():
    while True:
        Pin3.on()
        sleep_us(HALF)
        Pin3.off()
        sleep_us(HALF)

# ---------------------------------------------------------
# FUNCION DE CAPTURA - compilada a codigo ARM nativo
# 300 MHz + @native + locals + temporizador acumulativo
# para alcanzar exactamente 8 kHz (125 us/muestra)
# ---------------------------------------------------------
@micropython.native
def capturar(a0, a1, a2, b1, b2):
    uk  = 0.0
    uk1 = 0.0
    uk2 = 0.0
    yk  = 0.0
    yk1 = 0.0
    yk2 = 0.0
    adc = ADC0.read_u16
    cf  = conversion_factor
    ent = ENTRADAS
    sal = SALIDAS
    _tu = ticks_us
    _td = ticks_diff
    _ta = ticks_add
    _su = sleep_us

    t_cap  = _tu()
    t_next = t_cap

    for i in range(500):
        yk = a0*uk + a1*uk1 + a2*uk2 + b1*yk1 + b2*yk2

        uk2 = uk1
        uk1 = uk
        yk2 = yk1
        yk1 = yk

        uk = adc() * cf
        ent[i] = uk
        sal[i] = yk

        t_next = _ta(t_next, 125)
        dt = _td(t_next, _tu())
        if dt > 0:
            _su(dt)

    total = _td(_tu(), t_cap)
    #print("Captura:", total, "us, prom:", total // 500, "us/muestra")

# ---------------------------------------------------------
# Arrancar hilo de onda cuadrada
# ---------------------------------------------------------
_thread.start_new_thread(Onda_Cuadrada, ())

# ---------------------------------------------------------
# BUCLE PRINCIPAL
# ---------------------------------------------------------
while True:
    if UART0.any() > 0:
        sleep_ms(100)
        LLAVE = UART0.read()

        if LLAVE and LLAVE[0] == 0x55:
            To_CTE_A0[0:4] = LLAVE[1:5]
            To_CTE_A1[0:4] = LLAVE[5:9]
            To_CTE_A2[0:4] = LLAVE[9:13]
            To_CTE_B1[0:4] = LLAVE[13:17]
            To_CTE_B2[0:4] = LLAVE[17:21]
            To_FREQ[0:4]   = LLAVE[21:25]

            CTE_A0 = struct.unpack('<f', bytes(To_CTE_A0))[0]
            CTE_A1 = struct.unpack('<f', bytes(To_CTE_A1))[0]
            CTE_A2 = struct.unpack('<f', bytes(To_CTE_A2))[0]
            CTE_B1 = struct.unpack('<f', bytes(To_CTE_B1))[0]
            CTE_B2 = struct.unpack('<f', bytes(To_CTE_B2))[0]
            FREQ   = struct.unpack('<f', bytes(To_FREQ))[0]

            PERIODO = (1/FREQ)
            HALF    = int((PERIODO*1000000)/2)
            print("Nuevos coeficientes cargados")
            print("Coeficientes recibidos:")
            print("  A0 = {}".format(CTE_A0))
            print("  A1 = {}".format(CTE_A1))
            print("  A2 = {}".format(CTE_A2))
            print("  B1 = {}".format(CTE_B1))
            print("  B2 = {}".format(CTE_B2))
            print("  FREQ = {} Hz".format(FREQ))

        if LLAVE and 0x52 in LLAVE:
            capturar(CTE_A0, CTE_A1, CTE_A2, CTE_B1, CTE_B2)

            for i in range(500):
                struct.pack_into('f', En_Bytes, i*8, ENTRADAS[i])
                struct.pack_into('f', En_Bytes, i*8+4, SALIDAS[i])

            for j in range(0, 4000, 50):
                UART0.write(En_Bytes[j:j+50])
                sleep_ms(60)
