# ProyectoFinalGALAGA - Invaderoids en MicroPython

Juego estilo Galaga/Space Invaders portado de C++ (JunkboxArcade) a MicroPython
para Raspberry Pi Pico 2W con pantalla ILI9341 TFT 320x240.

## Materiales

- Raspberry Pi Pico 2W
- LCD TFT 2.8" IPS SPI HD 320x240 (ILI9341)
- Buzzer pasivo
- 4 botones pulsadores (Push Buttons)
- Resistencias pull-down no necesarias (se usan pull-up internos)
- Cables dupont / protoboard

## Conexiones

### Pantalla ILI9341 (SPI0)

| Pin ILI9341 | Pin Pico 2W | GPIO |
|-------------|-------------|------|
| VCC         | 3V3 (pin 36)| -    |
| GND         | GND (pin 38)| -    |
| CS          | GP17 (pin 22)| 17  |
| RESET       | GP21 (pin 27)| 21  |
| DC/RS       | GP20 (pin 26)| 20  |
| SDI/MOSI    | GP19 (pin 25)| 19  |
| SCK         | GP18 (pin 24)| 18  |
| LED         | 3V3 (pin 36)| -    |
| SDO/MISO    | GP16 (pin 21)| 16  |

### Botones (con pull-up interno)

| Boton    | Pin Pico 2W | GPIO |
|----------|-------------|------|
| Izquierda| GP2 (pin 4) | 2    |
| Derecha  | GP3 (pin 5) | 3    |
| Disparo  | GP4 (pin 6) | 4    |
| Pausa    | GP5 (pin 7) | 5    |

Cada boton conecta el GPIO a GND cuando se presiona.

### Buzzer

| Buzzer | Pin Pico 2W  | GPIO |
|--------|------------- |------|
| +      | GP15 (pin 20)| 15   |
| -      | GND (pin 18) | -    |

## Archivos a copiar al Pico 2W

Usando Thonny, copiar los siguientes archivos a la raiz del Pico 2W:

```
/
|-- main.py
|-- game.py
|-- player.py
|-- enemy.py
|-- bullet.py
|-- asteroid.py
|-- button.py
|-- buzzer.py
|-- colours.py
|-- ili9341.py          (de la carpeta micropython-ili9341/)
|-- sprites/
|   |-- __init__.py
|   |-- sprites.py
```

## Como ejecutar en Thonny

1. Conectar el Raspberry Pi Pico 2W por USB
2. Abrir Thonny IDE
3. Seleccionar interprete: MicroPython (Raspberry Pi Pico)
4. Copiar todos los archivos listados arriba al Pico 2W
   - Click derecho en cada archivo > "Upload to /"
   - Crear la carpeta "sprites" en el Pico primero
5. El archivo `main.py` se ejecuta automaticamente al encender el Pico
6. Para ejecutar manualmente: abrir main.py y presionar F5

## Controles del juego

- **Izquierda**: Mover nave a la izquierda
- **Derecha**: Mover nave a la derecha
- **Disparo**: Disparar (mantener presionado para fuego rapido)
- **Pausa**: Pausar/Reanudar el juego

## Mecanicas del juego

- 3 filas x 8 columnas de enemigos
- Puntuacion: Fila 0 = 30pts, Fila 1 = 20pts, Fila 2 = 10pts
- Dive Bomber (nave especial) = 50pts
- Guardian (power-up): al tocarlo da +1 vida (maximo 3)
- Asteroide: esquivarlo, destruye enemigos tambien
- 5 tranches por nivel, 10 niveles de dificultad (cíclicos)
- El juego termina cuando los enemigos llegan al fondo o se pierden todas las vidas
