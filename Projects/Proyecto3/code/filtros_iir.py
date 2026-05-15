# =============================================================
# Sistema de Filtros Digitales IIR - Raspberry Pi Pico 2W
#
# =============================================================

from machine import Pin, ADC, PWM
import _thread
import time
import sys
import select

# =============================================================
# PARAMETROS DEL SISTEMA
# =============================================================

FS_LP = 8000                
PERIOD_US_LP = 125          
PRINT_SKIP_LP = 2           


FS_HP = 1000                  
PERIOD_US_HP = 1000         
PRINT_SKIP_HP = 1           

# =============================================================
# CONFIGURACION DE HARDWARE
# =============================================================
adc = ADC(Pin(26))          # ADC0 leyendo la señal física real
pwm_sq = PWM(Pin(3))        # Onda cuadrada física generada en el Pin 3
pwm_sq.freq(50)             
pwm_sq.duty_u16(32768)      # 50% ciclo de trabajo

# =============================================================
# COEFICIENTES - FILTRO PASA BAJAS
# =============================================================
LP_A0 =  0.0303
LP_A1 =  0.0303
LP_B1 =  0.9394

# =============================================================
# COEFICIENTES - FILTRO PASA ALTAS
# =============================================================
HP_A0 =  0.8889
HP_A1 = -0.8889
HP_B1 =  0.7778

# =============================================================
# ESTADO COMPARTIDO
# =============================================================
st = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0]

RUN  = 0
FILT = 1
LU1  = 2
LY1  = 3
HU1  = 4
HY1  = 6
SU   = 8
SY   = 9
ND   = 10

# =============================================================
# NUCLEO 1: ECUACION EN DIFERENCIAS 
# =============================================================
def filter_core(st, adc_obj, tm,
                lp_a0, lp_a1, lp_b1,
                hp_a0, hp_a1, hp_b1,
                period_lp, period_hp, skip_lp, skip_hp):
    
    counter_lp = 0
    counter_hp = 0

    while True:
        t0 = tm.ticks_us()

        if st[0] == 1:       
            
            # Lectura del hardware físico (Pin 26)
            raw = adc_obj.read_u16()
            u_k = raw / 65535.0    

            if st[1] == 0:       
                y_k = lp_a0 * u_k + lp_a1 * st[2] + lp_b1 * st[3]
                st[2] = u_k      
                st[3] = y_k      
                
                counter_lp += 1
                if counter_lp >= skip_lp:
                    st[8] = u_k      
                    st[9] = y_k      
                    st[10] = 1       
                    counter_lp = 0
                    
                current_period = period_lp
                
            else:
              
                y_k = hp_a0 * u_k + hp_a1 * st[4] + hp_b1 * st[6]
                st[4] = u_k      
                st[6] = y_k      
                
                counter_hp += 1
                if counter_hp >= skip_hp:
                    st[8] = u_k      
                    st[9] = y_k      
                    st[10] = 1       
                    counter_hp = 0
                
                current_period = period_hp
        else:
            current_period = period_lp if st[1] == 0 else period_hp

        # Heartbeat de temporización
        elapsed = tm.ticks_diff(tm.ticks_us(), t0)
        if elapsed < current_period:
            tm.sleep_us(current_period - elapsed)

# =============================================================
# INICIAR NUCLEO 1 
# =============================================================
_thread.start_new_thread(filter_core, (
    st, adc, time,
    LP_A0, LP_A1, LP_B1,
    HP_A0, HP_A1, HP_B1,
    PERIOD_US_LP, PERIOD_US_HP, PRINT_SKIP_LP, PRINT_SKIP_HP
))

# =============================================================
# NUCLEO 0: COMUNICACION SERIAL NO BLOQUEANTE 
# =============================================================
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

print("\n" + "=" * 50)
print("  Filtro pasa bajas y pasa altas.)")
print("=" * 50)
print("Comandos disponibles:")
print("  START       - Iniciar filtrado")
print("  LP          - Pasa Bajas")
print("  HP          - Pasa Altas ")
print("  FREQ <hz>   - Frecuencia")
print("  STATUS      - Estado actual")
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
                    st[HY1] = 0.0
                print("OK: Filtrado detenido")
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
                st[HY1] = 0.0
                print("OK: Pasa Altas Seleccionado")
            elif cmd.startswith("FREQ"):
                parts = cmd.split()
                if len(parts) >= 2:
                    try:
                        freq = int(parts[1])
                        if freq < 20:
                            print("ERR: Frecuencia no soportada por la Pico")
                        else:
                            pwm_sq.freq(freq)
                            print("OK")
                    except ValueError:
                        print("ERR: Frecuencia no valida")
            elif cmd == "STATUS":
                if st[FILT] == 0:
                    print("Modo: Pasa Bajas | Estado: {} | PWM: {} Hz".format(
                        "Activo" if st[RUN] == 1 else "Detenido", pwm_sq.freq()))
                else:
                    print("Modo: Pasa Altas | Estado: {} | PWM: {} Hz".format(
                        "Activo" if st[RUN] == 1 else "Detenido", pwm_sq.freq()))
            else:
                print("ERR: Comando desconocido")
        elif ch:
            cmd_buf += ch

    if st[ND] == 1:
        st[ND] = 0
        print("{:.4f},{:.4f}".format(st[SU], st[SY]))

    time.sleep_us(200)