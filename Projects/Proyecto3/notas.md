# Contexto
## Consideraciones para los resultados del filtro Digital

Para diseñar el filtro con las carácteristicas de interés (se eligieron de manera libre y arbitraría) 

* Primer orden, frecuencia de corte $f_c = 500 [Hz]$
* Segundo orden, frecuencia de corte $f_c = 800 [Hz]$

### ¿Como se implemento un filtro?

El filtro es de primer orden debido a que solo se tiene un elemento que almacena energía (capacitor) (*filtro RC*)

Se calculan los valores para construir el circuito RC, ya con los valores de la resistencia y el capacitor se puede obtener su función de transferencia.

Sin embargo como la señal de entrada (señal de cuadrada) es una señal análogica, la Rasberry la lee a partir de su convertidor Analógico -> Digital, es decir la señal de entrada esta en dominio discreto, por lo que se debe obtener la función de diferencia en tiempo discreto (Discretización de Transformada Bilineal)

Es a partir de esta discretización que se logra obtener la ecuación en diferencias (*fórmula recursiva que calcula el estado actual de un sistema basándose en la información que ocurrió en los pasos anteriores*) dado su naturaleza esta ya se puede implementar en la pico.

Es por esto que se realiza todo los calculos para obtener las ecuaciones en diferencias y posteriormente implementarlas en python

# Para hacer los resultados

Hay que documentar principalmente el comportamiento observado en las gráficas cubriendo principalmente dos puntos
1. Que el filtro funcione, si es un pasa bajas que solo deje pasar las bajas jsjs
2. Comparar $V_{in}$ (señal cuadrada) con la señal de salida $V_{out}$ ya filtrada


Para el primer punto, ya se encuentra explicado eso de manera resumida en la tabla

## Filtro 1

Se tienen que poner las gráficas obtenidas para multiples frecuencias $50,200,500,1000,2000$ 

Se debe explicar que en la entrada pare frecuencias bajas, se observa bien que es una señal cuadrada debido a que su frecuencia es baja (alterna muy lento) y cuando es alta al alternar muy rapido se parece a una señal triangular

## Explicar Graficas

**Entrada**: En pocas palabras es explicar porque se ve asi la onda cuadrada dependiendo su frecuencia y en la salida parafrasear lo de la tabla.

**Salida**: Aqui hay que considerar lo que se vio en SISCOM 🤓

Como estamos metiendo de entrada una señal cuadrada, dicha señal cuadrada se compone de la suma de señales senoidales con diferentes frecuencias,  es por esto que en las gráficas vemos que hay partes de la señal que el filtro si deja pasar y otras no. 

Entonces pues parafrasar la tabla al colocar las imagenes (solo colocar 1 de las que se encuentran dentro de la carpeta,) y describir la saldia

**Hacer lo mismo** para el filtro de segundo orden

## Indicar las diferencias entre el Filtro de Segundo Orden

A parte de que son diferentes tipos de filtro (pasa-bajas) y (pasa-altas), escribir un parrafo breve sobre como es la atenuación en cada filtro

La diferencia principal es que entre mayor sea el orden del filtro realizará una atenuación más invasiva
* Primer Orden: Transición suave y lenta
* Segundo Orden; Transición abrupta y mas rapida

Compararlo con dos graficas donde en uno se vea del primer orden esa transicion suave y en otra abrupta

Por último mencionar que esto igual se puede ver representado al obtener la ecuación en diferencias donde en primer orden solo se tiene 1 entrada ($u(k-1)$)
y otra de salida ($y(k-1)$), de forma que para hacer los calculos solo mira un valor atras (ya calculado). Mientras que para el de segundo orden se requiere el doble, de forma que el filtro de segundo orden implica más calculos.






