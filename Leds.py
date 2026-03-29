from machine import Pin
import time
import _thread

pines_leds = [Pin(i, Pin.OUT) for i in range(8)]

Decision = '000'

def set_leds(valor):
    for i in range(8):
        pines_leds[i].value((valor >> i) & 1)


def leer_entradas():
    global Decision
    Entradas = ['000', '001', '010', '011', '100', '101', '110', '111']
    
    print(f'\nEntradas: {Decision} - Todos los LEDs apagados')
    
    while True:
        nueva_opcion = input('\nTeclee la combinacion de entradas [PIN11, PIN15, PIN17]: ')
        
        if nueva_opcion in Entradas:
            
            Decision = nueva_opcion
            
            if Decision == '000':
                print(f'Entradas: {Decision} - Todos los LEDs apagados')
            elif Decision == '001':
                print(f'Entradas: {Decision} - Encender – Apagar LED’s')
            elif Decision == '010':
                print(f'Entradas: {Decision} - Encender – Apagar Nibbles')
            elif Decision == '011':
                print(f'Entradas : {Decision} - Corrimientos entre Nibbles a la derecha')
            elif Decision == '100':
                print(f'Entradas : {Decision} - Corrimientos entre Nibbles a la izquierda')
            elif Decision == '101':
                print(f'Entradas: {Decision} - Corrimientos de LED’s a la derecha.')
            elif Decision == '110':
                print(f'Entradas: {Decision} - Corrimientos de LED’s a la izquierda.')
            elif Decision == '111':
                print(f'Entradas: {Decision} - Corrimientos de LED’s en Zig – Zag.')
            else:
                print(f'Cambio detectado -> Ejecutando combinacion: {Decision}')
        else:
            print('Opcion no valida, recuerde, entradas disponibles 000,001,010,011,100,101,110,111.')

if __name__ == "__main__":
    
    paso=0
    
    _thread.start_new_thread(leer_entradas, ())
    
    while True:
        if Decision == '000':
            set_leds(0b00000000)
            time.sleep(0.1)
            
        elif Decision == '001':
            set_leds(0b11111111)
            time.sleep(0.2)
            set_leds(0b00000000)
            time.sleep(0.2)
            
        elif Decision == '010':
            set_leds(0b11110000)
            time.sleep(0.2)
            set_leds(0b00001111)
            time.sleep(0.2)
            
        elif Decision == '011':
            secuencia = [0b11001100, 0b01100110, 0b00110011, 0b10011001]
            for valor in secuencia:
                set_leds(valor)
                time.sleep(0.2)
                if Decision != '011':
                    break
        elif Decision == '100':
            secuencia = [0b10011001, 0b00110011, 0b01100110, 0b11001100]
            for valor in secuencia:
                set_leds(valor)
                time.sleep(0.2)
                if Decision != '100':
                    break
        elif Decision == '101':
            secuencia = [0b10000000, 0b01000000, 0b00100000, 0b00010000, 0b00001000, 0b00000100, 0b00000010, 0b00000001]
            for valor in secuencia:
                set_leds(valor)
                time.sleep(0.2)
                if Decision != '101':
                    break
        elif Decision == '110':
            secuencia = [0b00000001, 0b00000010, 0b00000100, 0b00001000, 0b00010000, 0b00100000, 0b01000000, 0b10000000]
            for valor in secuencia:
                set_leds(valor)
                time.sleep(0.2)
                if Decision != '110':
                    break
        elif Decision == '111':
            secuencia = [0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1]
            posicion = secuencia[paso % len(secuencia)]
            set_leds(1 << posicion)
            paso += 1
            time.sleep(0.2)