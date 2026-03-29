from machine import Pin
import time
import _thread

pines_leds = [Pin(i, Pin.OUT) for i in range(8)]

Decision = '000'

def set_leds(valor):
    for i in range(8):
        pines_leds[i].value((valor >> i) & 1)

def mostrar_menu():
    print("\n" + "="*60)
    print(" " * 18 + "CONTROL DE LEDs")
    print("="*60)
    print("  [000] - Todos los LEDs apagados")
    print("  [001] - Encender / Apagar LEDs")
    print("  [010] - Encender / Apagar Nibbles")
    print("  [011] - Corrimientos entre Nibbles a la derecha")
    print("  [100] - Corrimientos entre Nibbles a la izquierda")
    print("  [101] - Corrimientos de LEDs a la derecha")
    print("  [110] - Corrimientos de LEDs a la izquierda")
    print("  [111] - Corrimientos de LEDs en Zig - Zag")
    print("="*60)

def leer_entradas():
    global Decision
    Entradas = ['000', '001', '010', '011', '100', '101', '110', '111']
    
    mostrar_menu()
    print(f'\nESTADO INICIAL: [{Decision}] - Todos los LEDs apagados')
    
    while True:
        nueva_opcion = input('\n>> Teclee la combinacion [PIN11, PIN15, PIN17]: ')
        
        if nueva_opcion in Entradas:
            Decision = nueva_opcion
            
            print("\n" + "-"*60)
            if Decision == '000':
                print(f'   Ejecutando: [{Decision}] - Todos los LEDs apagados')
            elif Decision == '001':
                print(f'   Ejecutando: [{Decision}] - Encender / Apagar LEDs')
            elif Decision == '010':
                print(f'   Ejecutando: [{Decision}] - Encender / Apagar Nibbles')
            elif Decision == '011':
                print(f'   Ejecutando: [{Decision}] - Corrimientos entre Nibbles (Derecha)')
            elif Decision == '100':
                print(f'   Ejecutando: [{Decision}] - Corrimientos entre Nibbles (Izquierda)')
            elif Decision == '101':
                print(f'   Ejecutando: [{Decision}] - Corrimientos de LEDs (Derecha)')
            elif Decision == '110':
                print(f'   Ejecutando: [{Decision}] - Corrimientos de LEDs (Izquierda)')
            elif Decision == '111':
                print(f'   Ejecutando: [{Decision}] - Corrimientos de LEDs en Zig-Zag')
            print("-" * 60)
        else:
            print("\n" + "!"*60)
            print("   Opcion no valida.")
            print("   Entradas disponibles: 000, 001, 010, 011, 100, 101, 110, 111")
            print("!"*60)

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

