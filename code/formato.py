ANCHO_MENU = 42


def linea_horizontal():
    return "+" + "-" * ANCHO_MENU + "+"


def linea_con_texto(texto):
    espacios = ANCHO_MENU - len(texto) - 2
    return "|  " + texto + " " * max(espacios, 0) + "|"


def linea_vacia():
    return "|" + " " * ANCHO_MENU + "|"



def imprimir_menu():
    print(linea_vacia())
    print(linea_con_texto("[2] Ecuacion de segundo grado"))
    print(linea_con_texto("    ax^2 + bx + c = 0"))
    print(linea_vacia())
    print(linea_con_texto("[3] Ecuacion de tercer grado"))
    print(linea_con_texto("    ax^3 + bx^2 + cx + d = 0"))
    print(linea_vacia())
    print(linea_con_texto("[0] Salir"))
    print(linea_vacia())
    print(linea_horizontal())


def imprimir_separador():
    print("-" * (ANCHO_MENU + 2))


def formatear_coeficiente(valor, variable, es_primero):
    if valor == 0:
        return ""
    signo = ""
    if es_primero:
        signo = "-" if valor < 0 else ""
    else:
        signo = " - " if valor < 0 else " + "
    valor_abs = abs(valor)
    if variable == "":
        parte_num = str(int(valor_abs)) if valor_abs == int(valor_abs) else str(valor_abs)
    elif valor_abs == 1:
        parte_num = ""
    else:
        parte_num = str(int(valor_abs)) if valor_abs == int(valor_abs) else str(valor_abs)
    return signo + parte_num + variable


def construir_ecuacion_cuadratica(coef_a, coef_b, coef_c):
    terminos = []
    terminos.append(formatear_coeficiente(coef_a, "x^2", len(terminos) == 0))
    terminos.append(formatear_coeficiente(coef_b, "x", len(terminos) == 0 or all(t == "" for t in terminos)))
    terminos.append(formatear_coeficiente(coef_c, "", len(terminos) == 0 or all(t == "" for t in terminos)))
    return "".join(t for t in terminos if t) + " = 0"


def construir_ecuacion_cubica(coef_a, coef_b, coef_c, coef_d):
    terminos = []
    terminos.append(formatear_coeficiente(coef_a, "x^3", len(terminos) == 0))
    terminos.append(formatear_coeficiente(coef_b, "x^2", len(terminos) == 0 or all(t == "" for t in terminos)))
    terminos.append(formatear_coeficiente(coef_c, "x", len(terminos) == 0 or all(t == "" for t in terminos)))
    terminos.append(formatear_coeficiente(coef_d, "", len(terminos) == 0 or all(t == "" for t in terminos)))
    return "".join(t for t in terminos if t) + " = 0"


def formatear_raiz(raiz_compleja):
    parte_real = raiz_compleja.real
    parte_imag = raiz_compleja.imag
    if abs(parte_real) < 1e-9:
        parte_real = 0.0
    if abs(parte_imag) < 1e-9:
        parte_imag = 0.0
    if parte_imag == 0.0:
        return "{:.4f}".format(parte_real)
    else:
        signo = "+" if parte_imag >= 0 else "-"
        return "{:.4f} {} {:.4f}i".format(parte_real, signo, abs(parte_imag))


def imprimir_resultados(raices):
    print()
    print(linea_horizontal())
    print(linea_con_texto("RESULTADOS"))
    print(linea_horizontal())
    for indice, raiz in enumerate(raices):
        print("  x{} = {}".format(indice + 1, formatear_raiz(raiz)))
    print()
