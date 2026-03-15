import cmath
from formato import formatear_raiz, construir_ecuacion_cuadratica, imprimir_separador


def mostrar_proceso_cuadratica(coef_a, coef_b, coef_c, discriminante, raiz_discriminante, raiz_1, raiz_2):
    ecuacion = construir_ecuacion_cuadratica(coef_a, coef_b, coef_c)
    print()
    imprimir_separador()
    print("  PROCESO DE CALCULO")
    imprimir_separador()
    print("  Ecuacion: {}".format(ecuacion))

    print()
    print("  Paso 1: Calcular discriminante")
    print("    D = b^2 - 4ac")
    valor_b2 = coef_b ** 2
    valor_4ac = 4 * coef_a * coef_c
    print("    D = ({})^2 - 4({})({})".format(coef_b, coef_a, coef_c))
    print("    D = {} - {} = {}".format(valor_b2, valor_4ac, discriminante))

    if discriminante > 0:
        print("    D > 0 => Dos raices reales distintas")
    elif discriminante == 0:
        print("    D = 0 => Dos raices reales iguales")
    else:
        print("    D < 0 => Dos raices complejas conjugadas")

    print()
    print("  Paso 2: Aplicar formula general")
    print("    x = (-b +/- sqrt(D)) / (2a)")
    denominador = 2 * coef_a
    print("    x = (-({}) +/- sqrt({})) / (2*{})".format(coef_b, discriminante, coef_a))
    print("    x = ({} +/- {}) / {}".format(-coef_b, formatear_raiz(raiz_discriminante), denominador))

    print()
    print("  Paso 3: Obtener raices")
    print("    x1 = {}".format(formatear_raiz(raiz_1)))
    print("    x2 = {}".format(formatear_raiz(raiz_2)))


def resolver_cuadratica(coef_a, coef_b, coef_c, mostrar_pasos=False):
    if coef_a == 0:
        return None, "Error: No es una ecuacion de segundo grado (a=0)."

    discriminante = coef_b ** 2 - 4 * coef_a * coef_c
    raiz_discriminante = cmath.sqrt(discriminante)

    raiz_1 = (-coef_b + raiz_discriminante) / (2 * coef_a)
    raiz_2 = (-coef_b - raiz_discriminante) / (2 * coef_a)

    if mostrar_pasos:
        mostrar_proceso_cuadratica(coef_a, coef_b, coef_c, discriminante, raiz_discriminante, raiz_1, raiz_2)

    return (raiz_1, raiz_2), None
