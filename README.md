# Proyecto Final - Microcomputadoras

## Archivos de la libreria micropython-ili9341 necesarios

De la carpeta `micropython-ili9341/`, copiar los siguientes archivos
a la raiz del Raspberry Pi Pico 2W:

### Archivo obligatorio

| Archivo       | Descripcion                                      |
|---------------|--------------------------------------------------|
| `ili9341.py`  | Driver principal del display ILI9341 (SPI, 320x240) |

### Archivos opcionales (solo si se necesitan)

| Archivo            | Descripcion                                 |
|--------------------|---------------------------------------------|
| `xglcd_font.py`    | Soporte para fuentes personalizadas XGLCD   |
| `xpt2046.py`       | Driver para pantalla tactil XPT2046         |
| `touch_keyboard.py`| Teclado virtual en pantalla tactil           |

### Para el proyecto GALAGA solo se necesita

```
ili9341.py
```

Este archivo contiene todas las funciones necesarias:
- `Display(spi, cs, dc, rst, width, height, rotation)` - Inicializacion
- `display.clear(color)` - Limpiar pantalla
- `display.draw_sprite(buf, x, y, w, h)` - Dibujar sprites
- `display.draw_pixel(x, y, color)` - Dibujar pixel individual
- `display.fill_hrect(x, y, w, h, color)` - Rectangulo relleno
- `display.draw_text8x8(x, y, text, color, bg)` - Texto con fuente integrada 8x8
- `display.draw_hline(x, y, w, color)` - Linea horizontal
- `display.draw_vline(x, y, h, color)` - Linea vertical

## Estructura del proyecto

```
ProyectoTeoria/
|   |-- README.md            # Instrucciones del juego
|   |-- main.py              # Punto de entrada
|   |-- game.py              # Logica principal del juego
|   |-- player.py            # Clase del jugador
|   |-- enemy.py             # Clase de enemigos
|   |-- bullet.py            # Clase de balas
|   |-- asteroid.py          # Asteroide, Guardian, DiveBomber
|   |-- button.py            # Manejo de botones con debounce
|   |-- buzzer.py            # Sonido PWM
|   |-- colours.py           # Constantes de color RGB565
|   |-- sprites/
|       |-- __init__.py
|       |-- sprites.py       # Datos de sprites en bytearray
|-- micropython-ili9341/     # Libreria del display
|-- JunkboxArcade/           # Codigo fuente original en C++
|-- document/                # Documento LaTeX del proyecto
|-- data/                    # Datasheets
```
