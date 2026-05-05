# Proyecto: Filtros digitales IIR con Raspberry Pi Pico 2W

Este repositorio contiene el reporte en LaTeX y el codigo MicroPython para implementar y analizar filtros IIR en una Raspberry Pi Pico 2W. El documento incluye el diseno matematico, las ecuaciones en diferencias y el analisis de resultados con senal cuadrada.

## Contenido principal

- main.tex: documento principal que integra portada, desarrollo, resultados y conclusiones.
- desarrollo.tex: derivacion de filtros pasa bajas y pasa altas, bilineal, coeficientes y ecuaciones en diferencias. Incluye un resumen de resultados.
- resultados.tex: tablas y figuras de comportamiento esperado y pruebas con onda cuadrada.
- portada.tex y referencias.bib: portada y bibliografia.
- img/ y portada_img/: imagenes del reporte.
- code/filtros_iir.py: firmware MicroPython para el filtrado en la Pico 2W.

## Contenido adicional

- documents/: scripts y ejemplos de apoyo (MicroPython, MATLAB y utilidades).
- Projects/Proyecto1 y Projects/Proyecto2: proyectos independientes con su propio main.tex, codigo e imagenes.

## Diseno actual de filtros (alineado con el codigo)

- Pasa bajas 1er orden (RC), fs = 8000 Hz:
	- fc ≈ 79.6 Hz
	- A0 = A1 = 0.0303, B1 = 0.9394
- Pasa altas 1er orden (RC), fs = 8000 Hz:
	- fc = 500 Hz
	- A0 = 0.8341, A1 = -0.8341, B1 = 0.6682

Las ecuaciones en diferencias se documentan en desarrollo.tex y se implementan en code/filtros_iir.py.

## Uso del codigo MicroPython

1. Conectar GP3 (PWM) a GP26 (ADC0) con un cable puente.
2. Cargar code/filtros_iir.py en la Pico 2W.
3. Usar comandos por puerto serial:
	 - START / STOP
	 - LP / HP
	 - FREQ <hz>
	 - STATUS
4. El programa imprime datos en formato "entrada,salida" para el Serial Plotter.

## Compilacion del reporte

Requiere una distribucion LaTeX con biber y latexmk.

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

Limpieza de auxiliares:

```bash
latexmk -c
```

Compilacion manual (si no usas latexmk):

```bash
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

## Notas de consistencia

- resultados.tex y algunas conclusiones en main.tex aun describen el diseno previo (LP de 500 Hz y HP de 800 Hz, 2do orden). Si necesitas coherencia total con el diseno actual, se recomienda actualizar esas secciones.
