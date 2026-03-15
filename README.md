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
├── code/                       # Codigos fuente en MicroPython
│   ├── main.py                 # Punto de entrada — menu principal e interaccion con el usuario
│   ├── solver_cuadratico.py    # Resolucion de ecuaciones cuadraticas (formula general)
│   ├── solver_cubico.py        # Resolucion de ecuaciones cubicas (metodo de Cardano)
│   └── formato.py              # Funciones de formato: menus, resultados, separadores y texto
├── img/                        # Imagenes utilizadas en el reporte LaTeX
├── portada_img/                # Escudos institucionales para la portada del reporte
│   ├── der.png                 # Logo derecho del encabezado
│   ├── izq.png                 # Logo izquierdo del encabezado
│   ├── escudounam_negro.jpg    # Escudo UNAM
│   └── escudofi_negro.jpg      # Escudo Facultad de Ingenieria
├── main.tex                    # Documento principal del reporte en LaTeX
├── portada.tex                 # Portada del reporte
├── referencias.bib             # Referencias bibliograficas (BibLaTeX / Biber)
├── main.pdf                    # PDF compilado del reporte
└── README.md                   # Este archivo
```

---

## Modulos del codigo

### `main.py`
Punto de entrada del programa. Contiene el menu interactivo que permite al usuario elegir
entre resolver una ecuacion cuadratica o cubica. Lee los coeficientes desde la terminal,
llama al solver correspondiente y muestra los resultados formateados.

### `solver_cuadratico.py`
Contiene la funcion `resolver_cuadratica(coef_a, coef_b, coef_c, mostrar_pasos)`.
Aplica la formula general $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$ usando `cmath.sqrt`
para soportar discriminantes negativos (raices complejas). Si `mostrar_pasos=True` imprime
el procedimiento detallado.

### `solver_cubico.py`
Contiene la funcion `resolver_cubica(coef_a, coef_b, coef_c, coef_d, mostrar_pasos)`.
Aplica el **metodo de Cardano**: reduce la cubica a forma deprimida calculando los parametros
$p$ y $q$, obtiene el discriminante de Cardano $D = (q/2)^2 + (p/3)^3$, calcula $u$ y $v$
con raiz cubica compleja, y reconstruye las tres raices usando las raices de la unidad.
Si `coef_a == 0` delega automaticamente a `resolver_cuadratica`.

### `formato.py`
Funciones auxiliares de presentacion: `imprimir_menu`, `imprimir_resultados`,
`imprimir_separador`, `formatear_raiz`, `construir_ecuacion_cuadratica` y
`construir_ecuacion_cubica`. Centralizan todo el formato de salida para mantener
el codigo de los solvers limpio.

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
