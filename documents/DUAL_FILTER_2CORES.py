##########################################################################################
##########################################################################################
####                                                                                  ####
####  FILTROS PASABANDAS QUE UTILIZAN LA ARQUITECTURA DUAL CORE DEL MICROCONTROLADOR  ####
####  RASPBERRY PI PICO 2 (RP2350), CUYOS EFECTOS DE SUS SALIDAS SERÁN SUMADOS PARA   ####
####  DAR EL EFECTO DE 2 CAMPANAS DE GAUSS EN EL DOMINIO DE LA FRECUENCIA.            ####
####                                                                                  ####
####  EN ESTE CASO, LA FILOSOFÍA DE LA ARQUITECTURA UTILIZA UN FILTRO IMPLEMENTADO    ####
####  EN CADA NUCLEO DE LA RP2350 Y LA SINCRONIZACIÓN SE REALIZA MEDIANTE EL USO DE   ####
####  UNA BANDERA QUE INDICA QUE LOS NUCLEOS TERMINARON EL ALGORITMO DE CADA FILTRO   ####
####  PARA REALIZAR ENTONCES LA SUMA DE AMBAS SALIDAS, REALIZANDO ASI SU TRANSMISIÓN  ####
####  DE LA SALIDA PARA LA VISUALIZACIÓN DE SUS RESPUESTAS.                           ####
####                                                                                  ####
####  LA ENTRADA DEL CANAL AN0 O AN1 SE REALIZARÁ PRIMERO Y SERÁ LA ENTRADA COMÚN     ####
####  PARA AMBOS FILTROS Y MADIANTE EL USO DE OTRA BANDERA, SE DARÁ INICIO A LA       ####
####  SOLUCIÓN DE LOS ALGORITMOS DE LOS FILTRO.                                       ####
####                                                                                  ####
##########################################################################################
##########################################################################################
####                                                                                  ####
####                     UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO                      ####
####                              FACULTAD DE INGENIERÍA                              ####
####                       DEPARTAMENTO DE CONTROL Y ROBÓTICA                         ####
####                                                                                  ####
##########################################################################################
##########################################################################################

from machine import Pin, Timer               # Importa librería de Pines.
from time import sleep, sleep_ms, sleep_us   # Importa librerías de retardos.
from machine import ADC,UART                 # Importa librerías del A/D y la UART.
import       _thread                         # Librería para poder utilizar
                                             # los 2 nucleos.
                                             
                                             
#OXOXOXOXOXOXOXOXOXOXOXOXOXOXOXOX#
# Convertir float a Hexadecimal  #
#OXOXOXOXOXOXOXOXOXOXOXOXOXOXOXOX#

import struct

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
# Hacer que la CPU trabaje a 240 Mhz #
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#

machine.freq(270000000)


#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
#  Declara el Factor de Conversión Adaptado al Universo  #
#  Numérico de la Transformada "Z" (0 - +1.0).           #
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
conversion_factor = 1 / (65535)  # Factor para que el A/D este entre
                                 # valores 0 y 1



########################################################################
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
########################################################################                                        
####                                                                ####                                        
####          CONFIGURA EL CANAL ADC0 DEL CONVERTIDOR A/D.          ####
####                                                                ####
########################################################################
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
########################################################################

adc0  = ADC(Pin(27))                # Crea el objeto ADC (GPIO26) canal 0
P25   = Pin(25, Pin.OUT)            # Pin nativo de la tarjeta
                                    # como testigo.
                                    
BANDERA1 = 0
BANDERA2 = 0
SALIDA   = 0
                                    



####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####                                                                             ####
####  FILTRO DIGITAL BUTTERWORTH PASO BANDA CON FRECUENCIA CENTRAL DE 5 HZ Y UN  ####
####  ANCHO DE BANDA DE 1 HZ.                                                    ####
####                                                                             ####
####  DECLARACIÓN DE COEFICIENTES DE LA ECUACIÓN EN DIFERENCIAS                  ####
####  Y1(k) = A00*U1(k) + A01*U1(k-1) + A02*U1(k-2) + B01*Y1(k-1) + B02*Y1(k-2)  ####
####                                                                             ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####

A00   = +0.07295965
A01   = +0.0
A02   = -0.07295965
B01   = +1.31508699
B02   = -0.85408068546
U1K   = +0.0
U1K1  = +0.0
U1K2  = +0.0
Y1K   = +0.0
Y1K1  = +0.0
Y1K2  = +0.0


####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####                                                                             ####
####  FILTRO DIGITAL BUTTERWORTH PASO BANDA CON FRECUENCIA CENTRAL DE 10 HZ Y    ####
####  UN ANCHO DE BANDA DE 1 HZ.                                                 ####
####                                                                             ####
####  DECLARACIÓN DE COEFICIENTES DE LA ECUACIÓN EN DIFERENCIAS                  ####
####  Y2(k) = A10*U2(k) + A11*U2(k-1) + A12*U2(k-2) + B11*Y2(k-1) + B12*Y2(k-2)  ####
####                                                                             ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####

A10   = +0.072959657268266669971623628043744247407 
A11   = +0.0
A12   = -0.072959657268266669971623628043744247407 
B11   = +0.000000000000000113880755203199057491064
B12   = -0.854080685463466604545601512654684484005
U2K   = +0.0
U2K1  = +0.0
U2K2  = +0.0
Y2K   = +0.0
Y2K1  = +0.0
Y2K2  = +0.0



############################################################################
############################################################################
####                                                                    ####
####    DISEÑO DEL FILTRO DIGITAL QUE SE EJECUTARÁ POR EL 2DO NÚCLEO    ####
####    Y QUE CORRESPONDE A UN PASO BANDA CON FRECUENCIA CENTRAL DE     ####
####    5 HZ Y UNANCHO DE BANDA DE 1 HZ.                                ####
####                                                                    ####
############################################################################
############################################################################
def Filtro_BandPass_5Hz():
    while True:
        
        P25.on()
        global Y1K, Y1K1, Y1K2, U1K, U1K1, U1K2
        Y1K = A00*U1K + A01*U1K1 + A02*U1K2 + B01*Y1K1 + B02*Y1K2
    
        # Actualiza I/O para la próxima iteración
        U1K2 = U1K1
        U1K1 = U1K
        Y1K2 = Y1K1
        Y1K1 = Y1K


    

    


_thread.start_new_thread(Filtro_BandPass_5Hz,())  # Inicia el "thread" de la onda cuadrada.

while True:
    Y2K = A10*U2K + A11*U2K1 + A12*U2K2 + B11*Y2K1 + B12*Y2K2

    # Actualiza I/O para la próxima iteración
    U2K2 = U2K1
    U2K1 = U2K
    Y2K2 = Y2K1
    Y2K1 = Y2K
    

    SALIDA = Y1K + Y2K
       

    
    Read0 = adc0.read_u16() * conversion_factor  # Toma lectura del canal 0
                                                 # del ADC en volts reales.
    U1K = Read0
    U2K = Read0
    
    print((Read0,SALIDA))                        # Grafica y muestra datos.

    sleep(0.025)                                 # Retardo de 0.025 Seg que
                                                 # corresponde al tiempo
                                                 # de muestreo.
    P25.off()
    
    


