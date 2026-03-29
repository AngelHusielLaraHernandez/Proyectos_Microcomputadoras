# Proyecto 1 — Laboratorio de Microcomputadoras

> **Plataforma Raspberry Pi Pico (RP2040) — Programacion en MicroPython**

---

## Objetivo

Mediante la creacion de codigo en MicroPython, dar solucion a una ecuacion cuadratica de
segundo y tercer orden utilizando la **Raspberry Pi Pico**, donde los coeficientes de la
ecuacion se ingresan a traves de la terminal y el resultado se muestra en la misma terminal.

---

## Descripcion

El programa resuelve ecuaciones polinomiales de segundo (cuadratica) y tercer orden (cubica).
Para la cuadratica se aplica la **formula general**, y para la cubica se utiliza el
**metodo de Cardano**. Ambos solvers soportan resultados complejos, y opcionalmente pueden
mostrar el procedimiento paso a paso en la terminal.

---


## Estructura del proyecto

```
Proyecto1/
├── code/                       # Códigos fuente en MicroPython
│   ├── main.py                 # Punto de entrada — menú principal e interacción con el usuario
│   ├── solver_cuadratico.py    # Resolución de ecuaciones cuadráticas (fórmula general)
│   ├── solver_cubico.py        # Resolución de ecuaciones cúbicas (método de Cardano)
│   ├── formato.py              # Funciones de formato: menús, resultados, separadores y texto
│   └── Leds.py                 # Control de LEDs con menú interactivo (nuevo módulo)
├── img/                        # Imágenes utilizadas en el reporte LaTeX
├── portada_img/                # Escudos institucionales para la portada del reporte
│   ├── der.png                 # Logo derecho del encabezado
│   ├── izq.png                 # Logo izquierdo del encabezado
│   ├── escudounam_negro.jpg    # Escudo UNAM
│   └── escudofi_negro.jpg      # Escudo Facultad de Ingeniería
├── main.tex                    # Documento principal del reporte en LaTeX
├── portada.tex                 # Portada del reporte
├── referencias.bib             # Referencias bibliográficas (BibLaTeX / Biber)
├── main.pdf                    # PDF compilado del reporte
└── README.md                   # Este archivo
```

---


## Módulos del código


### `Leds.py` (nuevo módulo)
Permite el control de 8 LEDs conectados a la Raspberry Pi Pico mediante un menú interactivo en terminal.
El usuario puede seleccionar diferentes combinaciones de entradas binarias para ejecutar patrones de encendido,
apagado, corrimientos y efectos visuales en los LEDs. El menú y los mensajes han sido mejorados para una interacción
más clara y estética. Ideal para prácticas de manejo de hardware y visualización de salidas digitales.

---

## Ejecucion

El codigo esta disenado para correr en una **Raspberry Pi Pico** con MicroPython.
Para probarlo en PC con Python 3 estandar, reemplazar `cmath` y `math` son identicos,
por lo que basta ejecutar desde la terminal:

```bash
python code/main.py
```

---

## Compilacion del reporte

```bash
# Compilacion completa (recomendado)
latexmk -pdf main.tex

# O manualmente
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

---

## Equipo

| Integrante |
|------------|
| Espinoza Matamoros Percival Ulises |
| Flores Colin Victor Jaziel |
| Garcia Cortes Adolfo de Jesus |
| Lara Hernandez Angel Husiel |
| Lugo Manzano Rodrigo |
