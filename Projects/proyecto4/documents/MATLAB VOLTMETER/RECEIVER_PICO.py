####################################################################################
####################################################################################
####                                                                            ####
####    RUTINA PARA RECIBIR UN DATO NUMÉRICO PROVEVIENTE DE UNA APP DISEÑADA    ####
####    EN MATLAB.                                                              ####
####                                                                            ####
####    NOTA: EL DATO SE RECIBE COMO UN STRING DE BYTES EN FORMATO "LITTLE      ####
####          ENDIAN" Y LUEGO ES CONVERTIDO A FORMATO "FLOAT" PARA LUEGO SER    ####
####          SER IMPRESO EN LA LÍNEA DE COMANDOS.                              ####
####                                                                            ####
####################################################################################
####################################################################################
####                                                                            ####
####                   UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO                  ####
####                      DEPARTAMENTO DE CONTROL Y ROBÓTICA                    ####
####                                     AÑO 2025                               ####
####                                                                            ####
####################################################################################
####################################################################################
####                                                                            ####
####               M. EN I. JOSÉ ANTONIO DE JESÚS ARREDONDO GARZA               ####
####                          EMAIL: jarredon@unam.mx                           ####
####                                                                            ####
####################################################################################
####################################################################################



from time import sleep, sleep_ms, sleep_us   # Importa librerías de retardos.
from machine import UART, Pin                # Importa librerías de UART y Pines.
import struct                                # Librería para manejo de datos
                                             # de "float" a "Little ENDIAN" y de
                                             # "Little ENDIAN" a "float". 
machine.freq(270000000)                      # Hacer que la CPU trabaje a 270 Mhz.



##*********************************************##
##  Declara UART0 a una tasa de 460800 Bauds,  ##
##  Tx = Pin0, Rx = Pin1. La UART0 será        ##
##  conectada al Módulo Bluetooth HC05.        ##
##*********************************************##
UART0       = UART(0, baudrate = 460800, tx = Pin(0), rx = Pin(1))


##******************************##
##  Pines Accesorio Utilizados  ##
##******************************##
P25         = Pin(25, Pin.OUT)    # Pin nativo de la tarjeta como testigo.


DATA    = [0]*4


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
            P25.on()               # Enciende el indicador de recepción.
                                                     
            ##xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx##
            ##                                            ##
            ##    DECODIFICA LOS DATOS "LITTLE ENDIAN"    ##
            ##                                            ##
            ##xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx##
            DATA[0] = LLAVE[1]
            DATA[1] = LLAVE[2]
            DATA[2] = LLAVE[3]
            DATA[3] = LLAVE[4]
            
            ##XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX##
            ##      CONVERSIÓN A "float"      ##
            ##XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX##
            CTE = struct.unpack('<f', bytes(DATA))

            print('La Constante Recibida es: ', CTE[0])