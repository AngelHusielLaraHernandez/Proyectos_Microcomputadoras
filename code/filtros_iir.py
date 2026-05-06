# =============================================================
# filtros_iir.py
# Sistema de Filtros Digitales IIR - Raspberry Pi Pico 2W
#
# Filtro 1 (LP): Pasa Bajas de 1er Orden (Intacto)
# Filtro 2 (HP): Pasa Altas (Ajustado a los coeficientes de tu captura)
#
# fs = 8000 Hz | T = 125 us
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

PRINT_SKIP_LP = 10           
PRINT_SKIP_HP = 15          

# =============================================================
# CONFIGURACION DE HARDWARE
# =============================================================
adc = ADC(Pin(26))          # GP26 = ADC0 (entrada analogica)
pwm_sq = PWM(Pin(3))        # GP3 = Onda cuadrada de prueba
pwm_sq.freq(50)             # Frecuencia inicial: 50 Hz
pwm_sq.duty_u16(32768)      # 50% duty cycle

# =============================================================
# COEFICIENTES - FILTRO PASA BAJAS (1er Orden)
# =============================================================
LP_A0 =  0.0303
LP_A1 =  0.0303
LP_B1 =  0.9394

# =============================================================
# COEFICIENTES - FILTRO PASA ALTAS 
# =============================================================
HP_A0 =  0.8341
HP_A1 = -0.8341
HP_A2 =  0.0
HP_B1 =  0.6682
HP_B2 =  0.0

# =============================================================
# ESTADO COMPARTIDO (Visible desde ambos cores)
# =============================================================
st = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0]

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
# =============================================================
def filter_core(st, adc_obj, tm,
                lp_a0, lp_a1, lp_b1,
                hp_a0, hp_a1, hp_a2, hp_b1, hp_b2,
                period, skip_lp, skip_hp):
    counter = 0

    while True:
        # 1. Registro de tiempo exacto al inicio del ciclo
        t0 = tm.ticks_us()

        # 2. Ejecucion matematica solo si la bandera RUN esta activa
        if st[0] == 1:       
            raw = adc_obj.read_u16()
            u_k = (raw / 65535.0) * 3.3

            if st[1] == 0:       
                # ---- Filtro Pasa Bajas ----
                y_k = lp_a0 * u_k + lp_a1 * st[2] + lp_b1 * st[3]
                st[2] = u_k      
                st[3] = y_k      
                current_skip = skip_lp
                
            else:
                # ---- Filtro Pasa Altas ----
                y_k = hp_a0 * u_k + hp_a1 * st[4] + hp_a2 * st[5] + hp_b1 * st[6] + hp_b2 * st[7]
                st[5] = st[4]    
                st[4] = u_k      
                st[7] = st[6]    
                st[6] = y_k      
                current_skip = skip_hp

            # 3. Peak Catcher dinamico 
            counter += 1
            if counter >= current_skip or (st[1] == 1 and abs(y_k - st[9]) > 0.8):
                st[8] = u_k      
                st[9] = y_k      
                st[10] = 1       
                counter = 0

        # 4. Heartbeat de sincronizacion: 
        # Garantiza el retraso exacto de 125us durante la ejecucion y al detenerse
        elapsed = tm.ticks_diff(tm.ticks_us(), t0)
        if elapsed < period:
            tm.sleep_us(period - elapsed)

# =============================================================
# INICIAR NUCLEO 1
# =============================================================
_thread.start_new_thread(filter_core, (
    st, adc, time,
    LP_A0, LP_A1, LP_B1,
    HP_A0, HP_A1, HP_A2, HP_B1, HP_B2,
    PERIOD_US, PRINT_SKIP_LP, PRINT_SKIP_HP
))

# =============================================================
# NUCLEO 0: COMUNICACION SERIAL NO BLOQUEANTE E IMPRESION
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
print("  LP          - Filtro pasa bajas")
print("  HP          - Filtro pasa altas (Ajustado a PDF)")
print("  FREQ <hz>   - Frecuencia de onda cuadrada")
print("  STATUS      - Estado actual del sistema")
print("=" * 50)

cmd_buf = ""

while True:
    if poll_obj.poll(0):
        ch = sys.stdin.read(1)
        if ch in ('\n', '\r'):
            cmd = cmd_buf.strip().upper()
            cmd_buf = ""

            if not cmd:
                pass
            elif cmd == "START":
                st[RUN] = 1
                print("OK: Filtrado iniciado")
            elif cmd == "STOP":
                st[RUN] = 0
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
                print("Comandos: START STOP LP HP FREQ <hz> STATUS")
                print("=" * 50)
            elif cmd == "LP":
                st[RUN] = 0
                st[FILT] = 0
                st[LU1] = 0.0
                st[LY1] = 0.0
                print("OK: Pasa Bajas Seleccionado")
            elif cmd == "HP":
                st[RUN] = 0
                st[FILT] = 1
                st[HU1] = 0.0
                st[HU2] = 0.0
                st[HY1] = 0.0
                st[HY2] = 0.0
                print("OK: Pasa Altas Seleccionado")
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
                nombre = "Pasa Bajas" if st[FILT] == 0 else "Pasa Altas"
                estado = "Activo" if st[RUN] == 1 else "Detenido"
                print("Filtro: {} | Estado: {} | fs: {} Hz | Onda Cuadrada: {} Hz".format(
                    nombre, estado, FS, pwm_sq.freq()))
            else:
                print("ERR: Comando desconocido: {}".format(cmd))
        elif ch:
            cmd_buf += ch

    if st[ND] == 1:
        st[ND] = 0
        print("{:.4f},{:.4f}".format(st[SU], st[SY]))

    time.sleep_us(200)