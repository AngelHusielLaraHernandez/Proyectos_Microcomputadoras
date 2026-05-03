# =============================================================
# filtros_iir.py
# Sistema de Filtros Digitales IIR - Raspberry Pi Pico 2W
#
# Filtro 1: Pasa Bajas de 1er Orden (IIR Butterworth, fc=500 Hz)
# Filtro 2: Pasa Altas de 2do Orden (Circuito RLC, fc=800 Hz)
#
# fs = 8000 Hz | T = 125 us
# Comunicación: USB Serial (COM5)
#
# Arquitectura de doble núcleo:
#   Núcleo 0: Comunicación serial y comandos
#   Núcleo 1: Ecuación en diferencias del filtro
# =============================================================

from machine import Pin, ADC, PWM
import _thread
import time

# =============================================================
# PARÁMETROS DEL SISTEMA
# =============================================================
FS = 8000                   # Frecuencia de muestreo (Hz)
PERIOD_US = 125             # Período de muestreo (us)

# =============================================================
# CONFIGURACIÓN DE HARDWARE
# =============================================================
adc = ADC(Pin(26))          # GP26 = ADC0 (entrada analógica)
pwm_sq = PWM(Pin(3))        # GP3 = Onda cuadrada de prueba
pwm_sq.freq(200)            # Frecuencia inicial: 200 Hz
pwm_sq.duty_u16(32768)      # 50% duty cycle
led = Pin("LED", Pin.OUT)   # LED indicador

# =============================================================
# COEFICIENTES - FILTRO PASA BAJAS (1er Orden, Butterworth)
# Circuito: RC serie (R=3.18k, C=100nF)
# fc = 500 Hz | Omega_a = tan(pi*500/8000) = 0.19891
# H(z) = 0.16591*(z + 1) / (z - 0.66818)
# y(k) = A0*u(k) + A1*u(k-1) + B1*y(k-1)
# =============================================================
LP_A0 =  0.16591
LP_A1 =  0.16591
LP_B1 =  0.66818

# =============================================================
# COEFICIENTES - FILTRO PASA ALTAS (2do Orden, RLC Butterworth)
# Circuito: RLC serie (C=390nF, R=680ohm, L=100mH), salida en L
# fc = 800 Hz | Omega_a = tan(pi*800/8000) = 0.32492
# H(z) = (0.63897*z^2 - 1.27795*z + 0.63897) /
#         (z^2 - 1.14305*z + 0.41286)
# y(k) = A0*u(k) + A1*u(k-1) + A2*u(k-2) + B1*y(k-1) + B2*y(k-2)
# =============================================================
HP_A0 =  0.63897
HP_A1 = -1.27795
HP_A2 =  0.63897
HP_B1 =  1.14305
HP_B2 = -0.41286

# =============================================================
# VARIABLES DE ESTADO
# =============================================================
# Pasa bajas (1er orden)
lp_u1 = 0.0        # u(k-1)
lp_y1 = 0.0        # y(k-1)

# Pasa altas (2do orden)
hp_u1 = 0.0        # u(k-1)
hp_u2 = 0.0        # u(k-2)
hp_y1 = 0.0        # y(k-1)
hp_y2 = 0.0        # y(k-2)

# Control
active_filter = 0   # 0 = Pasa Bajas, 1 = Pasa Altas
running = False

# =============================================================
# FUNCIÓN DEL MENÚ
# =============================================================
def mostrar_menu():
    print("\n" + "=" * 50)
    print("  Sistema de Filtros Digitales IIR")
    print("  Raspberry Pi Pico 2W | fs = {} Hz".format(FS))
    print("=" * 50)
    print("Comandos disponibles:")
    print("  START       - Iniciar filtrado")
    print("  STOP        - Detener filtrado")
    print("  LP          - Filtro pasa bajas (fc=500 Hz)")
    print("  HP          - Filtro pasa altas (fc=800 Hz)")
    print("  FREQ <hz>   - Frecuencia de onda cuadrada")
    print("  STATUS      - Estado actual del sistema")
    print("=" * 50)

# =============================================================
# NÚCLEO 1: ECUACIÓN EN DIFERENCIAS (ejecuta a fs = 8000 Hz)
# =============================================================
def filter_core():
    global lp_u1, lp_y1
    global hp_u1, hp_u2, hp_y1, hp_y2
    global active_filter, running

    while True:
        if not running:
            time.sleep_ms(1)
            continue

        t0 = time.ticks_us()

        # Lectura del ADC (16 bits: 0-65535)
        raw = adc.read_u16()
        u_k = (raw / 65535.0) * 3.3    # Conversión a voltaje (0-3.3V)

        if active_filter == 0:
            # ---- Filtro Pasa Bajas 1er Orden (RC) ----
            # y(k) = A0*u(k) + A1*u(k-1) + B1*y(k-1)
            y_k = LP_A0 * u_k + LP_A1 * lp_u1 + LP_B1 * lp_y1
            # Actualizar estados
            lp_u1 = u_k
            lp_y1 = y_k
        else:
            # ---- Filtro Pasa Altas 2do Orden (RLC) ----
            # y(k) = A0*u(k) + A1*u(k-1) + A2*u(k-2)
            #       + B1*y(k-1) + B2*y(k-2)
            y_k = (HP_A0 * u_k + HP_A1 * hp_u1 + HP_A2 * hp_u2
                   + HP_B1 * hp_y1 + HP_B2 * hp_y2)
            # Actualizar estados (orden importa)
            hp_u2 = hp_u1
            hp_u1 = u_k
            hp_y2 = hp_y1
            hp_y1 = y_k

        # Enviar datos por USB Serial: entrada,salida
        print("{:.4f},{:.4f}".format(u_k, y_k))

        # Esperar resto del período de muestreo
        elapsed = time.ticks_diff(time.ticks_us(), t0)
        if elapsed < PERIOD_US:
            time.sleep_us(PERIOD_US - elapsed)
        else:
            # Forzamos al Núcleo 1 a ceder el procesador (GIL) por un instante.
            # Esto evita que el Núcleo 0 se congele si el ciclo toma más de 125us.
            time.sleep_us(0)

# =============================================================
# INICIAR NÚCLEO 1
# =============================================================
_thread.start_new_thread(filter_core, ())

# =============================================================
# NÚCLEO 0: COMUNICACIÓN SERIAL Y COMANDOS
# =============================================================
mostrar_menu()

while True:
    try:
        line = input()                  # Lectura bloqueante (Core 0)
        cmd = line.strip().upper()

        if cmd == "START":
            running = True
            led.on()
            print("OK: Filtrado iniciado")

        elif cmd == "STOP":
            running = False
            led.off()
            print("OK: Filtrado detenido")
            mostrar_menu()              # Se vuelve a mostrar el menú inmediatamente

        elif cmd == "LP":
            active_filter = 0
            lp_u1 = 0.0
            lp_y1 = 0.0
            print("OK: Pasa Bajas 1er Orden (fc=500 Hz)")

        elif cmd == "HP":
            active_filter = 1
            hp_u1 = 0.0
            hp_u2 = 0.0
            hp_y1 = 0.0
            hp_y2 = 0.0
            print("OK: Pasa Altas 2do Orden (fc=800 Hz)")

        elif cmd.startswith("FREQ"):
            parts = cmd.split()
            if len(parts) >= 2:
                try:
                    freq = int(parts[1])
                    pwm_sq.freq(freq)
                    print("OK: Onda cuadrada = {} Hz".format(freq))
                except ValueError:
                    print("ERR: Frecuencia no valida")
            else:
                print("Uso: FREQ <frecuencia_hz>")

        elif cmd == "STATUS":
            nombre = "Pasa Bajas (fc=500Hz)" if active_filter == 0 \
                     else "Pasa Altas (fc=800Hz)"
            estado = "Activo" if running else "Detenido"
            frecuencia_onda = pwm_sq.freq() # Leemos la frecuencia actual del hardware
            
            print("Filtro: {} | Estado: {} | fs: {} Hz | Onda Cuadrada: {} Hz".format(
                nombre, estado, FS, frecuencia_onda))

        elif cmd != "":
            print("ERR: Comando desconocido: {}".format(line))

    except Exception as e:
        time.sleep_ms(100)