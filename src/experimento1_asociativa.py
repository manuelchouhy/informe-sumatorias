"""Experimento 1: propiedad asociativa.

La sucesión a_N = suma de (1 + b^k - b^k) para k = 1..N vale exactamente N en
aritmética real. Este módulo la evalúa con las tres asociaciones que pide la
consigna, con b de tipo int y de tipo float, y genera las figuras y tablas que
usa el informe. Ver docs/REQUISITOS.md, sección "Experimento 1".

Decisiones de implementación relevantes para el informe:

- Nunca se usa sum() de Python: los términos se acumulan con un for explícito.
- b^k se calcula multiplicando de a uno (potencia = potencia * b) y no con el
  operador **. Con floats, ** lanza OverflowError al superar el mayor número
  representable, mientras que la multiplicación sucesiva devuelve inf, que es
  justamente el comportamiento que el experimento quiere observar.
- Los desbordes no se atrapan: b^k llega a inf, el término inf - inf da NaN y
  a_N queda en NaN de ahí en adelante. Se grafica tal cual.
"""
import sys
import time

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np

import comun

# --- Parámetros del experimento -------------------------------------------------

N_MAX = 1000  # la consigna pide N = 1, 2, ..., 1000
BASES_ENTERAS = (2, 3, 5, 10)
BASES_FLOTANTES = (2.0, 3.0, 5.0, 10.0)
BASES_NEGATIVAS = (-2.0, -3.0, -5.0, -10.0)
BASES_HASTA_UNO = (0.0, 0.1, 0.5, 0.9, 1.0)  # BONUS: b <= 1
TAMANOS_COSTO = (1000, 5000, 10000, 20000, 50000, 100000)  # BONUS: costo de los enteros
REPETICIONES_COSTO = 3  # se informa el mínimo, que es la medida menos ruidosa

# Las tres asociaciones, en el orden en que las lista la consigna.
ETIQUETAS = (
    r"$1 + b^k - b^k$",
    r"$(1 + b^k) - b^k$",
    r"$(1 - b^k) + b^k$",
)
NOMBRES_CORTOS = ("A1", "A2", "A3")
COLORES = ("#1f77b4", "#ff7f0e", "#2ca02c")
ESTILOS = ("-", "--", ":")
ANCHOS = (3.4, 2.0, 1.6)

MASCARA_64 = (1 << 64) - 1
LIMITE_64 = 1 << 63


# --- Núcleo del experimento -----------------------------------------------------

def terminos(n: int, b: int | float) -> tuple[list, list, list]:
    """Los términos 1 + b^k - b^k para k = 1..n, uno por cada asociación.

    Devuelve tres listas paralelas, en el orden de ETIQUETAS. El tipo de los
    términos sigue al de b: con b entero la aritmética es exacta y todos valen 1.
    """
    es_entero = isinstance(b, int)
    uno = 1 if es_entero else 1.0
    potencia = uno  # b^0
    primera, segunda, tercera = [], [], []
    for _ in range(n):
        potencia = potencia * b  # b^k a partir de b^(k-1), sin usar **
        primera.append(uno + potencia - potencia)
        segunda.append((uno + potencia) - potencia)
        tercera.append((uno - potencia) + potencia)
    return primera, segunda, tercera


def sumas_parciales(n: int, b: int | float) -> tuple[list, list, list]:
    """Las sucesiones a_1, a_2, ..., a_n para las tres asociaciones.

    Acumula con un for explícito, nunca con sum().
    """
    cero = 0 if isinstance(b, int) else 0.0
    parciales = []
    for serie in terminos(n, b):
        acumulado = cero
        valores = []
        for termino in serie:
            acumulado = acumulado + termino
            valores.append(acumulado)
        parciales.append(valores)
    return parciales[0], parciales[1], parciales[2]


def a_N(n: int, b: int | float) -> tuple:
    """La suma a_N para un único N, en las tres asociaciones.

    Es la función que pide el ítem 1 de la consigna: recibe N y b, devuelve los
    tres resultados.
    """
    return tuple(serie[-1] for serie in sumas_parciales(n, b))


def _envolver_int64(x: int) -> int:
    """Reduce x al rango de un entero con signo de 64 bits, en complemento a dos.

    Simula lo que hace el hardware con los enteros de tamaño fijo de C o Java,
    donde el desborde no lanza error sino que descarta los bits altos.
    """
    x &= MASCARA_64
    return x - (1 << 64) if x >= LIMITE_64 else x


def suma_int64(n: int, b: int) -> tuple[int, int, int]:
    """a_N calculada con enteros de 64 bits simulados, con desborde por truncamiento.

    Cada operación intermedia se reduce a 64 bits, igual que en un lenguaje con
    enteros de tamaño fijo.
    """
    acumuladores = [0, 0, 0]
    potencia = 1
    for _ in range(n):
        potencia = _envolver_int64(potencia * b)
        # Las dos primeras asociaciones coinciden: Python evalúa 1 + p - p de
        # izquierda a derecha, que es exactamente (1 + p) - p.
        primeras = _envolver_int64(_envolver_int64(1 + potencia) - potencia)
        valores = (
            primeras,
            primeras,
            _envolver_int64(_envolver_int64(1 - potencia) + potencia),
        )
        for i, valor in enumerate(valores):
            acumuladores[i] = _envolver_int64(acumuladores[i] + valor)
    return acumuladores[0], acumuladores[1], acumuladores[2]


def primer_desborde_int64(b: int, n: int = N_MAX) -> tuple[int | None, int, int]:
    """Primer k donde b^k deja de entrar en 64 bits, con el valor exacto y el truncado."""
    exacta, envuelta = 1, 1
    for k in range(1, n + 1):
        exacta = exacta * b
        envuelta = _envolver_int64(envuelta * b)
        if envuelta != exacta:
            return k, exacta, envuelta
    return None, exacta, envuelta


def _costo_una_corrida(n: int, b: int | float) -> int | float:
    """Acumula a_n y devuelve b^n, sin guardar la serie de sumas parciales.

    Se usa solo para medir tiempo y memoria en el BONUS de enteros grandes: no
    almacena las sumas parciales para que la medición refleje el costo de la
    aritmética y no el de armar listas.
    """
    es_entero = isinstance(b, int)
    uno = 1 if es_entero else 1.0
    potencia = uno
    acumulado = 0 if es_entero else 0.0
    for _ in range(n):
        potencia = potencia * b
        acumulado = acumulado + (uno + potencia - potencia)
    return potencia


# --- Diagnóstico ----------------------------------------------------------------

def umbral_teorico(b: float) -> int:
    """Mayor k tal que |b|^k < 2^53, calculado con enteros exactos.

    Mientras |b|^k queda por debajo de 2^53 el espaciado de los flotantes en esa
    zona es menor o igual a 1 y el 1 del término sobrevive a la suma.
    """
    limite = 1 << 53
    base = abs(int(b))
    if base <= 1:
        return N_MAX
    k, potencia = 0, 1
    while potencia * base < limite:
        potencia *= base
        k += 1
    return k


def diagnostico(n: int, b: int | float) -> dict:
    """Umbrales observados para una base: hasta dónde vale 1 cada término y cuándo hay inf.

    El desborde se busca con el mismo tipo que b: los enteros de Python no
    desbordan, así que con b entero no hay ningún k infinito.
    """
    series = terminos(n, b)
    ultimos = []
    for serie in series:
        k = 0
        for valor in serie:
            if valor != 1:
                break
            k += 1
        ultimos.append(k)
    es_entero = isinstance(b, int)
    potencia = 1 if es_entero else 1.0
    primer_inf = None
    if not es_entero:
        for k in range(1, n + 1):
            potencia = potencia * b
            if potencia in (float("inf"), float("-inf")):
                primer_inf = k
                break
    return {"ultimo_k_correcto": ultimos, "primer_k_infinito": primer_inf}


# --- Figuras --------------------------------------------------------------------

def _por_filas(items: list, columnas: int) -> list:
    """Reordena las entradas de una leyenda para que se lean por filas.

    Matplotlib llena la leyenda por columnas; esta permutación deja las entradas
    en el orden en que se quieren leer.
    """
    filas = -(-len(items) // columnas)
    salida = []
    for columna in range(columnas):
        for fila in range(filas):
            indice = fila * columnas + columna
            if indice < len(items):
                salida.append(items[indice])
    return salida


def _figura_paneles(bases: tuple, nombre: str) -> None:
    """Figura de 2x2 paneles con a_N contra N, una base por panel y tres curvas por panel."""
    # El tamaño en pulgadas se elige cercano al ancho de texto del informe: así la
    # figura casi no se reduce al incluirla y las etiquetas siguen siendo legibles.
    fig, ejes = plt.subplots(2, 2, figsize=(7.4, 5.8), sharex=True, sharey=True)
    enes = np.arange(1, N_MAX + 1)
    hubo_desborde = False
    for eje, b in zip(ejes.flat, bases):
        eje.plot(enes, enes, color="0.6", lw=1.0, zorder=1)
        for serie, color, estilo, ancho in zip(sumas_parciales(N_MAX, b),
                                               COLORES, ESTILOS, ANCHOS):
            eje.plot(enes, np.asarray(serie, dtype=float),
                     color=color, ls=estilo, lw=ancho, zorder=2)
        info = diagnostico(N_MAX, b)
        if info["primer_k_infinito"] is not None:
            eje.axvline(info["primer_k_infinito"], color="0.35", lw=1.0, ls="-.", zorder=3)
            hubo_desborde = True
        eje.set_xscale("log")
        eje.set_yscale("log")
        eje.set_title(f"$b = {b:.1f}$" if isinstance(b, float) else f"$b = {b}$")
    for eje in ejes[-1]:
        eje.set_xlabel("$N$ (cantidad de términos)")
    for eje in ejes[:, 0]:
        eje.set_ylabel("$a_N$ (valor de la suma)")

    # Primero las tres asociaciones y después las referencias, para que la leyenda
    # muestre una fila por grupo.
    entradas = [(Line2D([], [], color=color, ls=estilo, lw=ancho), etiqueta)
                for etiqueta, color, estilo, ancho
                in zip(ETIQUETAS, COLORES, ESTILOS, ANCHOS)]
    entradas.append((Line2D([], [], color="0.6", lw=1.0), "$a_N = N$ (valor exacto)"))
    if hubo_desborde:
        entradas.append((Line2D([], [], color="0.35", lw=1.0, ls="-."),
                         r"primer $k$ con $b^k = \infty$"))
    handles, etiquetas = zip(*_por_filas(entradas, 3))
    fig.legend(handles, etiquetas, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.11))
    fig.tight_layout()
    comun.guardar_figura(fig, nombre)


# --- Tablas ---------------------------------------------------------------------

def _tabla_umbrales() -> None:
    """Umbrales de pérdida del 1 y de desborde, para bases positivas y negativas."""
    filas = []
    for b in BASES_FLOTANTES + BASES_NEGATIVAS:
        info = diagnostico(N_MAX, b)
        infinito = info["primer_k_infinito"]
        filas.append([f"${b:.1f}$", f"${umbral_teorico(b)}$"]
                     + [f"${k}$" for k in info["ultimo_k_correcto"]]
                     + [f"${infinito}$" if infinito is not None else "sin desborde"])
    comun.guardar_tabla(
        filas,
        [r"$b$", r"$k^\ast$ predicho", r"$1+b^k-b^k$",
         r"$(1+b^k)-b^k$", r"$(1-b^k)+b^k$", r"$k$ con $b^k=\infty$"],
        "exp1-umbrales")


def _tabla_bonus_hasta_uno() -> None:
    """BONUS: con b <= 1 el término se aparta del 1 a lo sumo en unos pocos épsilon."""
    filas = []
    for b in BASES_HASTA_UNO:
        series = terminos(N_MAX, b)
        desvios = []
        for serie in series:
            mayor = 0.0
            for valor in serie:
                desvio = abs(valor - 1.0)
                if desvio > mayor:
                    mayor = desvio
            desvios.append(mayor)
        finales = a_N(N_MAX, b)
        error_final = max(abs(valor - N_MAX) for valor in finales)
        filas.append([f"${b:.1f}$"]
                     + [comun.formato_cientifico(d) for d in desvios]
                     + [comun.formato_cientifico(error_final)])
    comun.guardar_tabla(
        filas,
        [r"$b$", r"$1+b^k-b^k$", r"$(1+b^k)-b^k$", r"$(1-b^k)+b^k$",
         r"$|a_{1000} - 1000|$"],
        "exp1-bonus-b-hasta-uno")


def _tabla_bonus_int64() -> None:
    """BONUS: qué pasa con enteros de tamaño fijo cuando b^k deja de entrar en 64 bits."""
    filas = []
    for b in BASES_ENTERAS:
        k, exacta, envuelta = primer_desborde_int64(b)
        resultados = suma_int64(N_MAX, b)
        filas.append([
            f"${b}$", f"${k}$",
            comun.formato_cientifico(float(exacta)),
            comun.formato_cientifico(float(envuelta)),
            f"${resultados[0]}$",
            f"${a_N(N_MAX, b)[0]}$",
        ])
    comun.guardar_tabla(
        filas,
        [r"$b$", r"$k$ del desborde", r"$b^k$ exacto", r"$b^k$ en 64 bits",
         r"$a_{1000}$ (64 bits)", r"$a_{1000}$ (Python)"],
        "exp1-bonus-int64")


def _tabla_bonus_costo() -> None:
    """BONUS: costo en tiempo y memoria de los enteros de precisión arbitraria."""
    filas = []
    for n in TAMANOS_COSTO:
        mejor_entero, potencia = float("inf"), 1
        for _ in range(REPETICIONES_COSTO):
            inicio = time.perf_counter()
            potencia = _costo_una_corrida(n, 10)
            mejor_entero = min(mejor_entero, time.perf_counter() - inicio)
        mejor_flotante = float("inf")
        for _ in range(REPETICIONES_COSTO):
            inicio = time.perf_counter()
            _costo_una_corrida(n, 10.0)
            mejor_flotante = min(mejor_flotante, time.perf_counter() - inicio)
        memoria = sys.getsizeof(potencia) / 1024
        filas.append([
            comun.formato_entero(n), comun.formato_entero(potencia.bit_length()),
            f"${memoria:.1f}$",
            f"${1000 * mejor_entero:.2f}$", f"${1000 * mejor_flotante:.2f}$",
            f"${mejor_entero / mejor_flotante:.0f}$",
        ])
    comun.guardar_tabla(
        filas,
        [r"$N$", r"bits de $b^N$", r"memoria de $b^N$ (KiB)", r"$t$ con int (ms)",
         r"$t$ con float (ms)", r"cociente"],
        "exp1-bonus-costo-enteros")


# --- Punto de entrada -----------------------------------------------------------

def correr() -> None:
    """Genera las figuras y tablas del experimento 1 e imprime un resumen corto."""
    _figura_paneles(BASES_ENTERAS, "exp1-asociaciones-int")
    _figura_paneles(BASES_FLOTANTES, "exp1-asociaciones-float")
    _figura_paneles(BASES_NEGATIVAS, "exp1-bases-negativas")
    _tabla_umbrales()
    _tabla_bonus_hasta_uno()
    _tabla_bonus_int64()
    _tabla_bonus_costo()

    print("[experimento 1] propiedad asociativa")
    print(f"  b entero: a_{N_MAX} = {a_N(N_MAX, 10)} (exacto para las tres asociaciones)")
    for b in BASES_FLOTANTES:
        finales = a_N(N_MAX, b)
        info = diagnostico(N_MAX, b)
        texto = ", ".join(f"{nombre}={valor:g}" for nombre, valor
                          in zip(NOMBRES_CORTOS, finales))
        print(f"  b = {b:.1f}: a_{N_MAX} -> {texto}; "
              f"últimos k correctos {info['ultimo_k_correcto']}; "
              f"primer inf en k = {info['primer_k_infinito']}")
    print("  3 figuras y 4 tablas escritas en informe/figuras y informe/tablas")
