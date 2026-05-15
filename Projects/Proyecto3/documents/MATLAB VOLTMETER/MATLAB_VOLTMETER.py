############################################################################################
############################################################################################
####                                                                                    ####
####    RUTINA QUE LEE LOS CANALES AN0, AN1, AN2 DEL CONVERTIDOR ANALÓGICO - DIGITAL    ####
####    Y EL CANAL AN4 QUE CORRESPONDE AL MEDIDOR DE TEMPERTURA INTERNO.                ####
####                                                                                    ####
####    LUEGO DE REALIZAR LAS LECTURAS, SE ESTÁ HACIENDO UNA TRANSMISIÓN DE LOS         ####
####    UTILIZANDO LA UART0 DE LA RASPBERRY PI PICO A TRAVES DE UN MÓDULO BLUETOOTH     ####
####    TIPO "HC05", SINCRONIZANDO LA TRANSMISIÓN DE DATOS SE REALIZA CON LA            ####
####    RECEPCIÓN DEL CARACTER "U" (0x55).                                              ####
####                                                                                    ####
############################################################################################
############################################################################################
####                                                                                    ####
####          UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO - FACULTAD DE INGENIERÍA          ####
####                       DEPARTAMENTO DE CONTROL Y ROBÓTICA                           ####
####                                                                                    ####
############################################################################################
############################################################################################
####                                                                                    ####
####                   M. EN I. JOSÉ ANTONIO DE JESÚS ARREDONDO GARZA                   ####
####                              EMAIL: jarredon@unam.mx                               ####
####                                                                                    ####
####                                      AÑO 2025                                      ####
####                                                                                    ####
############################################################################################
############################################################################################


from machine import Pin, Timer               # Importa librería de Pines.
from time import sleep, sleep_ms, sleep_us   # Importa librerías de retardos.
from machine import ADC,UART                 # Importa librerías del A/D y la UART.
import       _thread                         # Librería para poder utilizar
                                             # los 2 nucleos.
import struct                                # Librería para manejo de datos
                                             # de "float" a "Little ENDIAN" y de
                                             # "Little ENDIAN" a "float".                                            
machine.freq(270000000)                      # Hacer que la CPU trabaje a 270 Mhz.




####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####                                     
####                                                                          ####                                        
####    CONFIGURACIÓN DEL CONVERTIDOR A/D PARA PODER LEER LOS CANALES AN0,    ####
####    AN1, AN2 Y AN3 (TEMPERATURA), LA GENERACIÓN DE UNA ONDA CUADRADA      ####
####    Y LA CONFIGURACIÓN DE LA UART0 DE LA RASPBERRY PI PICO/PICO2.         ####
####                                                                          ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####

AN0         = ADC(Pin(26))        # Define el objeto ADC (GPI26) del canal AN0.
AN1         = ADC(Pin(27))        # Define el objeto ADC (GPI27) del canal AN1.
AN2         = ADC(Pin(28))        # Define el objeto ADC (GPI28) del canal AN2.
SENSOR      = ADC(4)              # Declara el Canal que mide la Temperatura.
Cte_to_Volt = (3.3/65535)         # Constante para conversión a Voltios Reales.


##xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx##
##  Variable que contendrá los  ##
##  los bytes "Little ENDIAN"   ##
##  que se usarán para enviar   ##
##  a través de la UART0        ##
##xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx##
En_Bytes    = bytearray(16)


##*********************************************##
##  Declara UART0 a una tasa de 460800 Bauds,  ##
##  Tx = Pin0, Rx = Pin1. La UART0 será        ##
##  conectada al Módulo Bluetooth HC05.        ##
##*********************************************##
UART0       = UART(0, baudrate = 460800, tx = Pin(0), rx = Pin(1))   


##***************************************************************##
##  Pines Accesorio Utilizados y Frecuencia de la Onda Cuadrada  ##
##***************************************************************##
P25         = Pin(25, Pin.OUT)    # Pin nativo de la tarjeta como testigo.
Pin3        = Pin(3,  Pin.OUT)    # Pin de acción paralela (que generará una
                                  # onda cuadrada).
FREQ        = 1                   # Pon la frecuencia a 1 Hz.
Period      = (1/FREQ)            # Obten el periodo.
Half_Period = (Period/2)          # Obten el semi periodo.





############################################################################
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####                                                                    ####
####          RUTINA PARA GENERAR UNA ONDA CUADRADA EN PARALELO         ####
####                                                                    ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
############################################################################
def Onda_Cuadrada():
    while True:
        Pin3.on()                           # Pon en "1" al Pin GPIO3 de laa RP2.
        sleep(Half_Period)                  # Retardo del semiperiodo.
        Pin3.off()                          # Pon en "0" al Pin GPIO3 de la RP2.
        sleep(Half_Period)                  # Retardo del semiperiodo.





###########################################################################################
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
####                                                                                   ####
####        RUTINA QUE REALIZA LA LECTURA DE DATOS Y SU TRANSMISIÓN SINCRONIZADA       ####
####        UTILIZANDO EL PUERTO UART0 Y EL MÓDULO BLUETOOTH HC05.                     ####
####                                                                                   ####
####XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX####
###########################################################################################
        
_thread.start_new_thread(Onda_Cuadrada,())  # Inicia el "thread" de la onda cuadrada.

while True:
    P25.off()                               # Apaga el Led testigo.
    
    ##******************************##
    ##  ¿Hay algún byte pendiente?  ##
    ##       (En este caso Rx)      ##
    ##******************************##
    if UART0.any() > 0:
        LLAVE = UART0.read()                # Lee el caracter recibido o 
                                            # caracteres recibidos.
                                            
        ##xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx##
        ##                                               ##
        ##    Investiga si se recibió un caracter "U"    ##
        ##                                               ##
        ##xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx##
        if LLAVE[0] == 85:
            P25.on()                                  # Enciende el indicador de
                                                      # transmisión.
            Read0    = AN0.read_u16()*Cte_to_Volt     # Lee el Canal AN0 del A/D.
            Read1    = AN1.read_u16()*Cte_to_Volt     # Lee el Canal AN1 del A/D.
            Read2    = AN2.read_u16()*Cte_to_Volt     # Lee el Canal AN2 del A/D.
            Valor_T  = SENSOR.read_u16()*Cte_to_Volt  # Lee el Canal AN3 del A/D.
            GRADOS   = 27 - (Valor_T - 0.706)/0.001721  # Obten la Temperatura de
                                                      # la CPU (centigrados).
            print(Read0, Read1, Read2, GRADOS)

            ##*******************************************##
            ##   Conversión de los "floats" a formato    ##
            ##   "Little ENDIAN" para poder transmitir   ##
            ##   la información a MATLAB utilizando      ##
            ##   la UART0 vía Bluetooth HC05.            ##
            ##*******************************************##
            En_Bytes  = bytearray(struct.pack("f",Read0))
            En_Bytes  = En_Bytes + bytearray(struct.pack("f", Read1))
            En_Bytes  = En_Bytes + bytearray(struct.pack("f", Read2))
            En_Bytes  = En_Bytes + bytearray(struct.pack("f", GRADOS))
            
            ##XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX##
            ##                                              ##
            ##    TRANSMITE LA CADENA DE BYTES OBTENIDOS    ##
            ##                                              ##
            ##XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX##
            
            UART0.write(En_Bytes)

            P25.off()                                 # Apaga el indicador de
                                                      # transmisión.