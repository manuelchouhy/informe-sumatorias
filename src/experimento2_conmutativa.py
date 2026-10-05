"""Experimento 2: propiedad conmutativa.

La sucesión b_N = suma de 1/(k(k+1)) para k = 1..N vale exactamente N/(N+1) en
aritmética real. Este módulo la evalúa con los cuatro algoritmos de suma que
pide la consigna, mide el error relativo contra la forma cerrada y genera las
figuras y tablas que usa el informe. Ver docs/REQUISITOS.md, sección
"Experimento 2".

Decisiones de implementación relevantes para el informe:

- Nunca se usa sum() de Python ni las reducciones de NumPy: los cuatro
  algoritmos acumulan con un for explícito, porque lo que se estudia es
  justamente el orden en que se encadenan las sumas parciales.
- Los cuatro calculan el término con la misma expresión, 1.0 / (k * (k + 1)),
  donde k * (k + 1) es un entero exacto de Python. Así la única diferencia
  entre algoritmos es el orden de acumulación y no el redondeo del término.
- Los términos decrecen con k, de modo que recorrer k de 1 a N es sumar de
  mayor a menor módulo, y recorrerlo de N a 1 es sumar de menor a mayor.
- Las curvas de los órdenes crecientes (mayor a menor y Kahan) se calculan con
  un único barrido que anota las sumas parciales en los N de la grilla. El
  estado del acumulador en el paso k no depende de N, así que el resultado es
  idéntico bit a bit al de llamar la función con cada N por separado; esa
  igualdad se verifica en _verificar_trazas(). Sin este barrido, la grilla del
  rango grande costaría unos 5e8 términos por algoritmo.
- Los órdenes que dependen de N (menor a mayor y randomizada) sí se recalculan
  para cada N de la grilla. Eso hace que el experimento tarde unos dos minutos.
"""
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np

import comun

# --- Parámetros del experimento -------------------------------------------------

# Las dos grillas de N que pide la consigna.
RANGO_CHICO = tuple(range(10, 10_001, 10))          # N = 10, 20, ..., 10000
RANGO_GRANDE = tuple(range(1000, 1_000_001, 1000))  # N = 1000, 2000, ..., 1000000

N_DISPERSION = 1_000_000  # N grande donde se repite la suma randomizada
REPETICIONES = 50         # repeticiones de la suma randomizada, con semilla distinta
N_TABLA = (10, 100, 1000, 10_000, 100_000, 1_000_000)

CLAVE_EXPERIMENTO = 2  # primera clave de comun.generador, para no chocar con otros módulos

# Unidad de redondeo del formato binario de doble precisión: la mitad del épsilon
# de máquina. Es el piso del error relativo de cualquier operación bien redondeada.
U = 2.0 ** -53

ALGORITMOS = ("mayor a menor", "menor a mayor", "randomizada", "Kahan")
ETIQUETAS = (
    "mayor a menor módulo",
    "menor a mayor módulo",
    "randomizada",
    "Kahan",
)
COLORES = ("#d62728", "#1f77b4", "#ff7f0e", "#2ca02c")

# Los cuatro algoritmos comparten muchos puntos: menor a mayor y Kahan caen casi
# siempre en el mismo valor. Se dibujan del más tapado al que menos, con marcador
# decreciente, para que la superposición se vea en vez de esconderse.
ORDEN_DIBUJO = ("Kahan", "menor a mayor", "randomizada", "mayor a menor")
TAMANOS = {"Kahan": 4.0, "menor a mayor": 2.3, "randomizada": 2.8, "mayor a menor": 2.5}


# --- Los cuatro algoritmos de suma ----------------------------------------------

def suma_mayor_a_menor(n: int) -> float:
    """b_N sumando de mayor a menor módulo.

    Los términos 1/(k(k+1)) decrecen con k, así que recorrer k de 1 a N los
    procesa de mayor a menor.
    """
    acumulado = 0.0
    for k in range(1, n + 1):
        acumulado = acumulado + 1.0 / (k * (k + 1))
    return acumulado


def suma_menor_a_mayor(n: int) -> float:
    """b_N sumando de menor a mayor módulo, o sea recorriendo k de N a 1."""
    acumulado = 0.0
    for k in range(n, 0, -1):
        acumulado = acumulado + 1.0 / (k * (k + 1))
    return acumulado


def suma_randomizada(n: int, repeticion: int = 0) -> float:
    """b_N sumando los términos en un orden aleatorio.

    La consigna pide que las funciones reciban únicamente N. El segundo
    argumento es opcional y solo identifica la repetición: cada valor da una
    permutación distinta pero reproducible, derivada de la semilla maestra.
    """
    orden = comun.generador(CLAVE_EXPERIMENTO, n, repeticion).permutation(n) + 1
    acumulado = 0.0
    for k in orden.tolist():
        acumulado = acumulado + 1.0 / (k * (k + 1))
    return acumulado


def suma_kahan(n: int) -> float:
    """b_N con suma compensada de Kahan, recorriendo k de 1 a N.

    La variable de compensación arrastra la parte baja que se pierde en cada
    suma y la reinyecta en el término siguiente, de modo que el error no se
    acumula con la cantidad de términos.
    """
    acumulado = 0.0
    compensacion = 0.0
    for k in range(1, n + 1):
        termino = 1.0 / (k * (k + 1)) - compensacion
        parcial = acumulado + termino
        compensacion = (parcial - acumulado) - termino
        acumulado = parcial
    return acumulado


def valor_teorico(n: int) -> float:
    """La forma cerrada N/(N+1), redondeada una sola vez al dividir enteros exactos."""
    return n / (n + 1)


def error_relativo(aproximacion: float, n: int) -> float:
    """Error relativo de una suma numérica respecto de la forma cerrada."""
    teorico = valor_teorico(n)
    return abs(aproximacion - teorico) / abs(teorico)


# --- Trazas sobre una grilla de N -----------------------------------------------

def _traza_mayor_a_menor(enes: tuple) -> list:
    """Las sumas de mayor a menor para toda la grilla, en un único barrido."""
    valores, acumulado, siguiente = [], 0.0, 0
    for k in range(1, enes[-1] + 1):
        acumulado = acumulado + 1.0 / (k * (k + 1))
        if siguiente < len(enes) and k == enes[siguiente]:
            valores.append(acumulado)
            siguiente += 1
    return valores


def _traza_kahan(enes: tuple) -> list:
    """Las sumas de Kahan para toda la grilla, en un único barrido."""
    valores, acumulado, compensacion, siguiente = [], 0.0, 0.0, 0
    for k in range(1, enes[-1] + 1):
        termino = 1.0 / (k * (k + 1)) - compensacion
        parcial = acumulado + termino
        compensacion = (parcial - acumulado) - termino
        acumulado = parcial
        if siguiente < len(enes) and k == enes[siguiente]:
            valores.append(acumulado)
            siguiente += 1
    return valores


def _verificar_trazas() -> None:
    """Comprueba que las trazas coincidan bit a bit con las funciones públicas.

    Es la garantía de que el barrido único no cambia el resultado: si alguna vez
    dejara de coincidir, el experimento estaría midiendo otra cosa.
    """
    control = (10, 137, 1000, 4321)
    for nombre, traza, funcion in (
            ("mayor a menor", _traza_mayor_a_menor(control), suma_mayor_a_menor),
            ("Kahan", _traza_kahan(control), suma_kahan)):
        for n, valor in zip(control, traza):
            if valor != funcion(n):
                raise ValueError(
                    f"La traza de {nombre} difiere de la función en N = {n}: "
                    f"{valor!r} contra {funcion(n)!r}.")


def _errores(enes: tuple) -> dict:
    """Error relativo de los cuatro algoritmos sobre la grilla `enes`."""
    trazas = {
        "mayor a menor": _traza_mayor_a_menor(enes),
        "menor a mayor": [suma_menor_a_mayor(n) for n in enes],
        "randomizada": [suma_randomizada(n) for n in enes],
        "Kahan": _traza_kahan(enes),
    }
    return {nombre: np.array([error_relativo(valor, n)
                              for valor, n in zip(traza, enes)])
            for nombre, traza in trazas.items()}


def _dispersion_randomizada() -> tuple[np.ndarray, np.ndarray]:
    """Sumas y errores relativos de REPETICIONES corridas randomizadas con el mismo N."""
    sumas = np.array([suma_randomizada(N_DISPERSION, repeticion)
                      for repeticion in range(REPETICIONES)])
    errores = np.array([error_relativo(suma, N_DISPERSION) for suma in sumas])
    return sumas, errores


# --- Figuras --------------------------------------------------------------------

def _figura_error(errores_chico: dict, errores_grande: dict) -> None:
    """Error relativo contra N en los dos rangos, un panel por rango."""
    fig, ejes = plt.subplots(2, 1, figsize=(7.4, 6.8), sharey=True)
    paneles = (
        (ejes[0], RANGO_CHICO, errores_chico,
         r"(a) $N = 10, 20, \ldots, 10\,000$"),
        (ejes[1], RANGO_GRANDE, errores_grande,
         r"(b) $N = 1000, 2000, \ldots, 10^{6}$"),
    )
    for eje, enes, errores, titulo in paneles:
        x = np.asarray(enes, dtype=float)
        for nombre in ORDEN_DIBUJO:
            eje.plot(x, errores[nombre], ".", color=COLORES[ALGORITMOS.index(nombre)],
                     ms=TAMANOS[nombre], alpha=0.7, zorder=2)
        eje.plot(x, np.sqrt(x) * U, color="0.30", ls="--", lw=1.3, zorder=3)
        eje.axhline(U, color="0.55", ls=":", lw=1.3, zorder=3)
        eje.set_xscale("log")
        # symlog en lugar de log: los órdenes bien condicionados dan error
        # exactamente nulo para muchos N, y en escala logarítmica esos puntos
        # desaparecerían. La banda lineal cercana al cero los muestra.
        eje.set_yscale("symlog", linthresh=1e-17, linscale=0.45)
        eje.set_title(titulo)
        eje.set_ylabel("error relativo")
    ejes[-1].set_xlabel("$N$ (cantidad de términos)")

    entradas = [(Line2D([], [], color=color, ls="none", marker="o", ms=5), etiqueta)
                for etiqueta, color in zip(ETIQUETAS, COLORES)]
    entradas.append((Line2D([], [], color="0.30", ls="--", lw=1.3),
                     r"$\sqrt{N}\,u$"))
    entradas.append((Line2D([], [], color="0.55", ls=":", lw=1.3),
                     r"$u = 2^{-53}$"))
    handles, etiquetas = zip(*entradas)
    fig.legend(handles, etiquetas, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.10))
    fig.tight_layout()
    comun.guardar_figura(fig, "exp2-error-relativo")


def _figura_dispersion(errores: np.ndarray, deterministas: dict) -> None:
    """Dispersión del error relativo de la suma randomizada sobre REPETICIONES corridas.

    Los otros tres algoritmos son deterministas para un N fijo, así que aportan
    una línea horizontal cada uno. Las que coinciden se dibujan una sola vez con
    los dos nombres en la leyenda, para no esconder una debajo de la otra.
    """
    fig, (izquierda, derecha) = plt.subplots(
        1, 2, figsize=(7.4, 4.0), sharey=True,
        gridspec_kw={"width_ratios": [2.5, 1]})

    izquierda.plot(range(1, REPETICIONES + 1), errores, "o", ms=4.5,
                   color=COLORES[2], zorder=3)
    entradas = [(Line2D([], [], color=COLORES[2], ls="none", marker="o", ms=5),
                 f"randomizada, $N = 10^{{{int(np.log10(N_DISPERSION))}}}$")]
    grupos: dict = {}
    for nombre, valor in deterministas.items():
        grupos.setdefault(valor, []).append(nombre)
    for valor, nombres in grupos.items():
        # Una línea que representa a dos algoritmos no puede llevar el color de uno solo.
        color = COLORES[ALGORITMOS.index(nombres[0])] if len(nombres) == 1 else "0.35"
        izquierda.axhline(valor, color=color, ls="--", lw=1.4, zorder=2)
        etiqueta = " y ".join(ETIQUETAS[ALGORITMOS.index(n)] for n in nombres)
        if valor == 0.0:
            etiqueta += ": error nulo"
        entradas.append((Line2D([], [], color=color, ls="--", lw=1.4), etiqueta))

    # symlog para que las referencias con error exactamente nulo tengan lugar en el eje.
    izquierda.set_yscale("symlog", linthresh=1e-16, linscale=0.45)
    izquierda.set_xlabel("número de repetición")
    izquierda.set_ylabel("error relativo")

    bordes = np.logspace(np.log10(errores.min()), np.log10(errores.max()), 13)
    derecha.hist(errores, bins=bordes, orientation="horizontal",
                 color=COLORES[2], alpha=0.75)
    derecha.set_xlabel("repeticiones")

    handles, etiquetas = zip(*entradas)
    fig.legend(handles, etiquetas, loc="lower center", ncol=2,
               bbox_to_anchor=(0.5, -0.13))
    fig.tight_layout()
    comun.guardar_figura(fig, "exp2-dispersion-randomizada")


# --- Tablas ---------------------------------------------------------------------

def _tabla_errores() -> None:
    """Error relativo de los cuatro algoritmos en unos pocos N representativos."""
    filas = []
    for n in N_TABLA:
        valores = (suma_mayor_a_menor(n), suma_menor_a_mayor(n),
                   suma_randomizada(n), suma_kahan(n))
        filas.append([comun.formato_entero(n)]
                     + [comun.formato_cientifico(error_relativo(valor, n))
                        for valor in valores])
    comun.guardar_tabla(
        filas,
        [r"$N$", "mayor a menor", "menor a mayor", "randomizada", "Kahan"],
        "exp2-errores")


def _tabla_resumen(errores_chico: dict, errores_grande: dict) -> None:
    """Resumen de los cuatro algoritmos sobre las dos grillas completas.

    La tabla de errores puntuales muestra seis valores de N; esta resume los mil
    valores de cada grilla, que es de donde salen las afirmaciones del informe
    sobre el máximo y sobre cuántos N dan error exactamente nulo.
    """
    filas = []
    for nombre, etiqueta in zip(ALGORITMOS, ETIQUETAS):
        grande = errores_grande[nombre]
        filas.append([
            etiqueta,
            comun.formato_cientifico(errores_chico[nombre].max()),
            comun.formato_cientifico(grande.max()),
            f"${int(np.count_nonzero(grande == 0))}$ de ${len(grande)}$",
        ])
    comun.guardar_tabla(
        filas,
        ["algoritmo", r"máximo, $N \leq 10^{4}$", r"máximo, $N \leq 10^{6}$",
         r"$N$ con $E_\mathrm{rel} = 0$"],
        "exp2-resumen")


def _tabla_dispersion(sumas: np.ndarray, errores: np.ndarray) -> None:
    """Resumen de la dispersión de la suma randomizada para un mismo N grande."""
    filas = [
        ["repeticiones", f"${REPETICIONES}$"],
        [r"resultados $b_N$ distintos", f"${len(set(sumas.tolist()))}$"],
        [r"$E_\mathrm{rel}$ mínimo", comun.formato_cientifico(errores.min())],
        [r"$E_\mathrm{rel}$ mediana", comun.formato_cientifico(float(np.median(errores)))],
        [r"$E_\mathrm{rel}$ máximo", comun.formato_cientifico(errores.max())],
        [r"desvío estándar de $E_\mathrm{rel}$",
         comun.formato_cientifico(float(errores.std(ddof=1)))],
        [r"cociente máximo sobre mínimo", f"${errores.max() / errores.min():.3g}$"],
    ]
    comun.guardar_tabla(filas, ["magnitud", "valor"], "exp2-dispersion",
                        alineacion="lr")


# --- Punto de entrada -----------------------------------------------------------

def correr() -> None:
    """Genera las figuras y tablas del experimento 2 e imprime un resumen corto."""
    _verificar_trazas()
    errores_chico = _errores(RANGO_CHICO)
    errores_grande = _errores(RANGO_GRANDE)
    sumas, errores_dispersion = _dispersion_randomizada()
    deterministas = {
        "mayor a menor": error_relativo(suma_mayor_a_menor(N_DISPERSION), N_DISPERSION),
        "menor a mayor": error_relativo(suma_menor_a_mayor(N_DISPERSION), N_DISPERSION),
        "Kahan": error_relativo(suma_kahan(N_DISPERSION), N_DISPERSION),
    }

    _figura_error(errores_chico, errores_grande)
    _figura_dispersion(errores_dispersion, deterministas)
    _tabla_errores()
    _tabla_resumen(errores_chico, errores_grande)
    _tabla_dispersion(sumas, errores_dispersion)

    print("[experimento 2] propiedad conmutativa")
    for nombre in ALGORITMOS:
        chico, grande = errores_chico[nombre], errores_grande[nombre]
        print(f"  {nombre:>13}: error máximo {chico.max():.2e} (N hasta {RANGO_CHICO[-1]:g}), "
              f"{grande.max():.2e} (N hasta {RANGO_GRANDE[-1]:g}); "
              f"{int(np.count_nonzero(grande == 0))} de {len(grande)} exactos en el rango grande")
    print(f"  randomizada en N = {N_DISPERSION}: "
          f"{len(set(sumas.tolist()))} resultados distintos en {REPETICIONES} corridas, "
          f"error entre {errores_dispersion.min():.2e} y {errores_dispersion.max():.2e}")
    print("  2 figuras y 3 tablas escritas en informe/figuras y informe/tablas")
