from formato import imprimir_menu, imprimir_resultados, imprimir_separador
from solver_cuadratico import resolver_cuadratica
from solver_cubico import resolver_cubica


def preguntar_mostrar_proceso():
    respuesta = input("  Mostrar proceso? (s/n): ")
    return respuesta.lower() == 's'


def leer_coeficientes(nombres):
    print()
    imprimir_separador()
    print("  Ingresa los coeficientes:")
    imprimir_separador()
    coeficientes = []
    for nombre in nombres:
        valor = float(input("  {} = ".format(nombre)))
        coeficientes.append(valor)
    return coeficientes


def manejar_ecuacion_cuadratica():
    try:
        coeficientes = leer_coeficientes(["a", "b", "c"])
        coef_a, coef_b, coef_c = coeficientes

        mostrar_pasos = preguntar_mostrar_proceso()

        raices, error = resolver_cuadratica(coef_a, coef_b, coef_c, mostrar_pasos)

        if error:
            print(error)
        else:
            imprimir_resultados(raices)
    except ValueError:
        print("  Error: Ingresa unicamente valores numericos.")


def manejar_ecuacion_cubica():
    try:
        coeficientes = leer_coeficientes(["a", "b", "c", "d"])
        coef_a, coef_b, coef_c, coef_d = coeficientes

        mostrar_pasos = preguntar_mostrar_proceso()

        raices, error = resolver_cubica(coef_a, coef_b, coef_c, coef_d, mostrar_pasos)

        if error:
            print(error)
        else:
            imprimir_resultados(raices)
    except ValueError:
        print("  Error: Ingresa unicamente valores numericos.")


def main():
    while True:
        imprimir_menu()

        opcion = input("\n  Opcion: ")

        if opcion == '0':
            print()
            imprimir_separador()
            print("  Saliendo del programa...")
            imprimir_separador()
            break
        elif opcion == '2':
            manejar_ecuacion_cuadratica()
        elif opcion == '3':
            manejar_ecuacion_cubica()
        else:
            print("  Opcion no valida. Intenta de nuevo.")


main()
