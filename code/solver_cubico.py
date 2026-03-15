import math
import cmath
from formato import formatear_raiz, construir_ecuacion_cubica, imprimir_separador
from solver_cuadratico import resolver_cuadratica


def raiz_cubica_compleja(numero_complejo):
    if abs(numero_complejo.imag) < 1e-10:
        valor_real = numero_complejo.real
        if valor_real >= 0:
            return complex(valor_real ** (1 / 3))
        else:
            return complex(-(abs(valor_real) ** (1 / 3)))
    modulo, angulo = cmath.polar(numero_complejo)
    return cmath.rect(modulo ** (1 / 3), angulo / 3)


def mostrar_proceso_cubica(coef_a, coef_b, coef_c, coef_d,
                           parametro_p, parametro_q, discriminante_cardano,
                           valor_u, valor_v, raices):
    ecuacion = construir_ecuacion_cubica(coef_a, coef_b, coef_c, coef_d)
    print()
    imprimir_separador()
    print("  PROCESO DE CALCULO (Metodo de Cardano)")
    imprimir_separador()
    print("  Ecuacion: {}".format(ecuacion))

    print()
    print("  Paso 1: Reducir a forma deprimida  t^3 + pt + q = 0")
    print("    p = (3ac - b^2) / (3a^2)")
    print("    p = (3*{}*{} - ({})^2) / (3*({})^2)".format(coef_a, coef_c, coef_b, coef_a))
    print("    p = {}".format(parametro_p))
    print()
    print("    q = (2b^3 - 9abc + 27a^2*d) / (27a^3)")
    print("    q = {}".format(parametro_q))

    print()
    print("  Paso 2: Calcular discriminante de Cardano")
    print("    D = (q/2)^2 + (p/3)^3")
    print("    D = ({})^2 + ({})^3".format(parametro_q / 2, parametro_p / 3))
    print("    D = {}".format(discriminante_cardano))

    print()
    print("  Paso 3: Calcular u y v")
    print("    u = cbrt(-q/2 + sqrt(D))")
    print("    u = {}".format(formatear_raiz(valor_u)))
    print("    v = cbrt(-q/2 - sqrt(D))")
    print("    v = {}".format(formatear_raiz(valor_v)))

    print()
    print("  Paso 4: Revertir sustitucion (x = t - b/(3a))")
    offset = coef_b / (3 * coef_a)
    print("    Offset = b/(3a) = {}/(3*{}) = {:.4f}".format(coef_b, coef_a, offset))

    print()
    print("  Paso 5: Raices obtenidas")
    for indice, raiz in enumerate(raices):
        print("    x{} = {}".format(indice + 1, formatear_raiz(raiz)))


def resolver_cubica(coef_a, coef_b, coef_c, coef_d, mostrar_pasos=False):
    if coef_a == 0:
        return resolver_cuadratica(coef_b, coef_c, coef_d, mostrar_pasos)

    parametro_p = (3 * coef_a * coef_c - coef_b ** 2) / (3 * coef_a ** 2)
    parametro_q = (2 * coef_b ** 3 - 9 * coef_a * coef_b * coef_c + 27 * coef_a ** 2 * coef_d) / (27 * coef_a ** 3)

    discriminante_cardano = (parametro_q / 2) ** 2 + (parametro_p / 3) ** 3

    valor_u = raiz_cubica_compleja(-parametro_q / 2 + cmath.sqrt(discriminante_cardano))
    valor_v = raiz_cubica_compleja(-parametro_q / 2 - cmath.sqrt(discriminante_cardano))

    raiz_unidad_1 = complex(-0.5, math.sqrt(3) / 2)
    raiz_unidad_2 = complex(-0.5, -math.sqrt(3) / 2)

    solucion_t1 = valor_u + valor_v
    solucion_t2 = raiz_unidad_1 * valor_u + raiz_unidad_2 * valor_v
    solucion_t3 = raiz_unidad_2 * valor_u + raiz_unidad_1 * valor_v

    offset_cardano = coef_b / (3 * coef_a)
    raiz_1 = solucion_t1 - offset_cardano
    raiz_2 = solucion_t2 - offset_cardano
    raiz_3 = solucion_t3 - offset_cardano

    raices = (raiz_1, raiz_2, raiz_3)

    if mostrar_pasos:
        mostrar_proceso_cubica(coef_a, coef_b, coef_c, coef_d,
                               parametro_p, parametro_q, discriminante_cardano,
                               valor_u, valor_v, raices)

    return raices, None
