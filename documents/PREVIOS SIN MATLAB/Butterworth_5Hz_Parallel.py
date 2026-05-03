#####################################################################
#####################################################################
####                                                             ####
####    RUTINA PARA SIMULAR EN TIEMPO REAL UN FILTRO PASABANDA   ####
####    DE 2DO ORDEN, CON UNA FRECUENCIA CENTRAL DE 5 HERTZ Y    ####
####    UNA FRECUENCIA DE MUESTREO DE 40 HZ (Ts = 0.025 Seg),    ####
####    INCLUYENDO LA GENERACIÓN DE UNA ONDA CUADRADA EN EL PIN  ####
####    GPIO3 QUE ESTARÁ CONECTADO AL PIN GPIO26 QUE CORRESPONDE ####
####    AL CANAL AN0 DEL A/D.                                    ####
####                                                             ####
#####################################################################
#####################################################################
####                                                             ####
####          UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO            ####
####                  FACULTAD DE INGENIERÍA                     ####
####             DEPARTAMENTO DE CONTROL Y ROBÓTICA              ####
####                                                             ####
#####################################################################
#####################################################################
####                                                             ####
####       M. EN I. JOSÉ ANTONIO DE JESÚS ARREDONDO GARZA        ####
####                 EMAIL: jarredon@unam.mx                     ####
####                                                             ####
#####################################################################
#####################################################################
####                                                             ####
####                         AÑO 2024                            ####
####                                                             ####
#####################################################################
#####################################################################
####                                                             ####
####   LOS COEFICIENTES GENERADOS POR LA HERRAMIENTA "fdatool"   ####
####   DE MATLAB SON LOS SIGUIENTES:                             ####
####                                                             ####
####               0.07295965*Z^2 + 0*Z - 0.07295965             ####
####     H(z) = ----------------------------------------         ####
####               Z^2 -1.31508699*Z +   0.85408068546           ####
####                                                             ####
####   TRANSLADANDO DIRECTAMENTE LOS COEFICIENTES:               ####
####                                                             ####
####   A0 = +0.07295965                                          ####
####   A1 = +0.0                                                 ####
####   A2 = -0.07295965                                          ####
####   B1 = +1.31508699                                          ####
####   B2 = -0.85408068546                                       ####
####                                                             ####
#####################################################################
#####################################################################


#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
# Hacer que la CPU trabaje a 240 Mhz #
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
machine.freq(270000000)

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
# Carga librería del COnvertidor A/D #
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
from machine import ADC, Pin

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
# Carga la librería de retardos #
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
from time import sleep

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
# Importa la Librería de Hilos #
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
import       _thread                # Librería para poder utilizar
                                    # los 2 nucleos.

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
#  Declara el Factor de Conversión Adaptado al Universo  #
#  Numérico de la Transformada "Z" (0 - +1.0).           #
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
conversion_factor = 1 / (65535)  # Factor para que el A/D este entre
                                 # valores 0 y 1

####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####                                                                  ####
####  DECLARACIÓN DE COEFICIENTES DE LA ECUACIÓN EN DIFERENCIAS       ####
####  Y(k) = A0*U(k) + A1*U(k-1) + A2*U(k-2) + B1*Y(k-1) + B2*Y(k-2)  ####
####                                                                  ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####

A0   = +0.07295965
A1   = +0.0
A2   = -0.07295965
B1   = +1.31508699
B2   = -0.85408068546
UK   = +0.0
UK1  = +0.0
UK2  = +0.0
YK   = +0.0
YK1  = +0.0
YK2  = +0.0

ONDA   = 5.0           # Frecuencia de la Onda Cuadrada
                       # en Herzt.
Ts     = 1/(ONDA)      # Obten el periodo.
HALF   = (Ts)/2        # Obten el semiperiodo.



####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####                                                     ####
####    Configuración de Pines usados por las Rutinas    ####
####                                                     ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####

adc0  = ADC(Pin(26))        # Crea el objeto ADC (GPIO26) canal 0
Pin25 = Pin(25, Pin.OUT)    # Pin nativo de la tarjeta
                            # como testigo.
Pin3  = Pin(3,  Pin.OUT)    # Pin de acción paralela (que generará
                            # la onda cuadrada).
                            
                            
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####                                                     ####
####    Definición de la Rutina que usará el Núcleo 2    ####
####    para la Generación de un Onda Cuadrada con un    ####
####    Periodo Asignado del la Variable "HALF" que      ####
####    Corresponde al Semiperiodo dado en Segundos.     ####
####                                                     ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####                                                     ####
####    NOTA: Se está usando el Pin GPIO3 para la        ####
####          generación de la onda cuadrada y este      ####
####          Pin se deberá conectar al Pin GPIO26       ####
####          que es la entrada AN0 del Convertido       ####
####          A/D.                                       ####
####                                                     ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
def Onda_Cuadrada():
    while True:
        Pin25.on()                            # Pin testigo ON.
        Pin3.on()                             # Pon en "1" al Pin GPIO3 de laa RP2.
        sleep(HALF)                           # Retardo dado por HALF.
        Pin25.off()                           # Pin testigo OFF.
        Pin3.off()                            # Pon en "0" al Pin GPIO3 de la RP2.
        sleep(HALF)                           # Retardo dado por HALF.


####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####                                                                   ####
####  PROGRAMA PRINCIPAL PARA REALIZAR EL FILTRADO USANDO LA ECUACIÓN  ####
####  EN DIFERENCIAS:                                                  ####
####                                                                   ####
####  Y(K) = A0*U(k) + A1*U(k-1) + A2*U(k-2) + B1*y(k-1) + B2*Y(k-2)   ####
####                                                                   ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
        
_thread.start_new_thread(Onda_Cuadrada,())  # Inicia el "thread" de la onda cuadrada.

while True:
    YK = A0*UK + A1*UK1 + A2*UK2 + B1*YK1 + B2*YK2

    # Actualiza I/O para la próxima iteración
    UK2 = UK1
    UK1 = UK
    YK2 = YK1
    YK1 = YK
    Read0 = adc0.read_u16() * conversion_factor  # Toma lectura del canal 0
                                                 # del ADC en volts reales.
    UK = Read0                                   # Asigna el nuevo valor U(k).
    print((UK,YK))                               # Grafica y muestra datos.
    sleep(0.025)                                 # Retardo de 0.025 Seg que
                                                 # corresponde al tiempo
                                                 # de muestreo.
