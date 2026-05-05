# =============================================================
# filtros_iir.py
# Sistema de Filtros Digitales IIR - Raspberry Pi Pico 2W
#
# Filtro 1: Pasa Bajas de 1er Orden (IIR Butterworth, fc=500 Hz)
# Filtro 2: Pasa Altas de 2do Orden (Circuito RLC, fc=800 Hz)
#
# fs = 8000 Hz | T = 125 us
# Comunicacion: USB Serial (COM5)
#
# Arquitectura de doble nucleo:
#   Nucleo 0: Comunicacion serial (no bloqueante) e impresion
#   Nucleo 1: Ecuacion en diferencias del filtro
#
# SOLUCION AL BUG DE _thread EN RP2350:
# El Core 1 no puede ver nombres del modulo (globals).
# TODO lo que necesita el hilo se pasa como argumentos
# en _thread.start_new_thread(func, (arg1, arg2, ...)).
# =============================================================

from machine import Pin, ADC, PWM
import _thread
import time
import sys
import select

# =============================================================
# PARAMETROS DEL SISTEMA
# =============================================================
FS = 8000                   # Frecuencia de muestreo (Hz)
PERIOD_US = 125             # Periodo de muestreo (us)
PRINT_SKIP = 2              # Imprimir cada N muestras (4000 lineas/s)

# =============================================================
# CONFIGURACION DE HARDWARE
# =============================================================
adc = ADC(Pin(26))          # GP26 = ADC0 (entrada analogica)
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
# ESTADO COMPARTIDO - lista mutable (visible desde ambos cores)
# Se pasa por referencia al hilo como argumento.
#
# st[0]  = running       (0 o 1)
# st[1]  = active_filter (0=PB, 1=PA)
# st[2]  = lp_u1         u(k-1) del pasa bajas
# st[3]  = lp_y1         y(k-1) del pasa bajas
# st[4]  = hp_u1         u(k-1) del pasa altas
# st[5]  = hp_u2         u(k-2) del pasa altas
# st[6]  = hp_y1         y(k-1) del pasa altas
# st[7]  = hp_y2         y(k-2) del pasa altas
# st[8]  = shared_u      (ultimo valor u para imprimir)
# st[9]  = shared_y      (ultimo valor y para imprimir)
# st[10] = new_data      (0 o 1)
# =============================================================
st = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0]

# Indices con nombre para legibilidad
RUN  = 0
FILT = 1
LU1  = 2
LY1  = 3
HU1  = 4
HU2  = 5
HY1  = 6
HY2  = 7
SU   = 8
SY   = 9
ND   = 10

# =============================================================
# NUCLEO 1: ECUACION EN DIFERENCIAS
# Recibe TODO por argumento - no usa globals del modulo.
# =============================================================
def filter_core(st, adc_obj, tm,
                lp_a0, lp_a1, lp_b1,
                hp_a0, hp_a1, hp_a2, hp_b1, hp_b2,
                period, skip):
    counter = 0

    while True:
        if st[0] == 0:       # running?
            tm.sleep_ms(1)
            continue

        t0 = tm.ticks_us()

        # Lectura del ADC (16 bits: 0-65535)
        raw = adc_obj.read_u16()
        u_k = (raw / 65535.0) * 3.3    # Conversion a voltaje (0-3.3V)

        if st[1] == 0:       # active_filter == PB
            # ---- Filtro Pasa Bajas 1er Orden (RC) ----
            # y(k) = A0*u(k) + A1*u(k-1) + B1*y(k-1)
            y_k = lp_a0 * u_k + lp_a1 * st[2] + lp_b1 * st[3]
            st[2] = u_k      # lp_u1
            st[3] = y_k      # lp_y1
        else:
            # ---- Filtro Pasa Altas 2do Orden (RLC) ----
            # y(k) = A0*u(k) + A1*u(k-1) + A2*u(k-2)
            #       + B1*y(k-1) + B2*y(k-2)
            y_k = (hp_a0 * u_k + hp_a1 * st[4] + hp_a2 * st[5]
                   + hp_b1 * st[6] + hp_b2 * st[7])
            st[5] = st[4]    # hp_u2 = hp_u1
            st[4] = u_k      # hp_u1
            st[7] = st[6]    # hp_y2 = hp_y1
            st[6] = y_k      # hp_y1

        # Guardar datos para impresion (cada 'skip' muestras)
        counter += 1
        if counter >= skip:
            st[8] = u_k      # shared_u
            st[9] = y_k      # shared_y
            st[10] = 1       # new_data
            counter = 0

        # Esperar resto del periodo de muestreo
        elapsed = tm.ticks_diff(tm.ticks_us(), t0)
        if elapsed < period:
            tm.sleep_us(period - elapsed)

# =============================================================
# INICIAR NUCLEO 1 - pasar TODO como argumentos
# =============================================================
_thread.start_new_thread(filter_core, (
    st, adc, time,
    LP_A0, LP_A1, LP_B1,
    HP_A0, HP_A1, HP_A2, HP_B1, HP_B2,
    PERIOD_US, PRINT_SKIP
))

# =============================================================
# NUCLEO 0: COMUNICACION SERIAL NO BLOQUEANTE + IMPRESION
# =============================================================
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

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

cmd_buf = ""

while True:
    # --- Verificar entrada serial (NO bloqueante) ---
    if poll_obj.poll(0):
        ch = sys.stdin.read(1)
        if ch in ('\n', '\r'):
            cmd = cmd_buf.strip().upper()
            cmd_buf = ""

            if not cmd:
                pass

            elif cmd == "START":
                st[RUN] = 1
                led.on()
                print("OK: Filtrado iniciado")

            elif cmd == "STOP":
                st[RUN] = 0
                led.off()
                # Reiniciar estados del filtro activo
                if st[FILT] == 0:
                    st[LU1] = 0.0
                    st[LY1] = 0.0
                else:
                    st[HU1] = 0.0
                    st[HU2] = 0.0
                    st[HY1] = 0.0
                    st[HY2] = 0.0
                print("OK: Filtrado detenido")
                print("=" * 50)
                print("Comandos: START STOP LP HP FREQ<hz> STATUS")
                print("=" * 50)

            elif cmd == "LP":
                st[RUN] = 0
                led.off()
                st[FILT] = 0
                st[LU1] = 0.0
                st[LY1] = 0.0
                print("OK: Pasa Bajas 1er Orden (fc=500 Hz)")

            elif cmd == "HP":
                st[RUN] = 0
                led.off()
                st[FILT] = 1
                st[HU1] = 0.0
                st[HU2] = 0.0
                st[HY1] = 0.0
                st[HY2] = 0.0
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
                nombre = "Pasa Bajas (fc=500Hz)" if st[FILT] == 0 \
                         else "Pasa Altas (fc=800Hz)"
                estado = "Activo" if st[RUN] == 1 else "Detenido"
                print("Filtro: {} | Estado: {} | fs: {} Hz | Onda Cuadrada: {} Hz".format(
                    nombre, estado, FS, pwm_sq.freq()))

            else:
                print("ERR: Comando desconocido: {}".format(cmd))

        elif ch:
            cmd_buf += ch

    # --- Imprimir datos si hay nuevos ---
    if st[ND] == 1:
        st[ND] = 0
        print("{:.4f},{:.4f}".format(st[SU], st[SY]))

    time.sleep_us(200)
