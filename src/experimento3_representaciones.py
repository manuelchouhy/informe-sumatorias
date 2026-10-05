"""Experimento 3: representaciones de una suma.

Dos sucesiones, cada una escrita de dos maneras matemáticamente equivalentes:

    b_N = suma de 1/(k(k+1)) = suma de (1/k - 1/(k+1)), con forma cerrada N/(N+1)
    c_N = suma de 1/(sqrt(k^2+1) + k) = suma de (sqrt(k^2+1) - k), sin forma cerrada

El módulo mide el error relativo de las dos representaciones de b_N contra la
forma cerrada, la diferencia absoluta D_N entre las dos representaciones de c_N,
y los dos BONUS: las dos formas cerradas de b_N y los términos individuales de
c_N. Ver docs/REQUISITOS.md, sección "Experimento 3".

Decisiones de implementación relevantes para el informe:

- Nunca se usa sum() de Python ni las reducciones de NumPy: las cuatro sumas
  acumulan con un for explícito.
- Las cuatro representaciones son sumas del mismo término k recorriendo k de 1
  a N, así que las curvas sobre la grilla se calculan con un único barrido que
  anota las sumas parciales en cada N de la grilla. El estado del acumulador en
  el paso k no depende de N, de modo que el resultado es idéntico bit a bit al
  de llamar la función con cada N por separado; _verificar_trazas() lo comprueba.
- La resta sqrt(k^2+1) - k es exacta: los dos operandos están a menos de un
  factor dos uno del otro, así que vale el lema de Sterbenz. El error de esa
  representación no viene de la resta sino del redondeo previo de la raíz, que
  la resta deja al descubierto al cancelar las cifras altas. Por eso la cota del
  error relativo del término es 2 k^2 u y crece con k. Para k mayor que 2^26.5
  se suma el redondeo de k^2+1, que ya no es representable; ahí el término
  calculado como diferencia vale cero y la discusión no cambia.
- El primer k donde sqrt(k^2+1) devuelve exactamente k se busca binada por
  binada: dentro de una binada el espaciado de los flotantes es constante y la
  separación real 1/(2k) decrece, así que la condición es monótona y se puede
  bisecar. Escanear k de a uno hasta 2^26 costaría un minuto y no haría falta.
"""
import math
from fractions import Fraction

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np

import comun

# --- Parámetros del experimento -------------------------------------------------

# La grilla de N que pide la consigna, para b_N y para c_N.
RANGO_N = (1,) + tuple(range(10, 10_001, 10))  # N = 1, 10, 20, ..., 10000

N_TABLA = (1, 10, 100, 1000, 10_000)

# Unidad de redondeo del formato binario de doble precisión.
U = 2.0 ** -53

# BONUS de los términos: hasta dónde se escanea k de a uno para ubicar los
# primeros cruces, y la grilla logarítmica que se grafica.
K_FINO = 300_000
K_MAXIMO = 100_000_000
UMBRALES = (1e-12, 1e-10, 1e-8, 1e-6)

# BONUS de las formas cerradas: hasta dónde se cuentan las discrepancias.
N_CONTEO_CERRADAS = 100_000
N_ERROR_CERRADAS = 20_000

COLOR_ESTABLE = "#1f77b4"     # representación que no cancela
COLOR_SUSCEPTIBLE = "#d62728"  # representación susceptible a cancelación
COLOR_COTA = "0.30"


# --- Las dos representaciones de b_N --------------------------------------------

def b_producto(n: int) -> float:
    """b_N sumando los términos 1/(k(k+1)).

    El producto k(k+1) es un entero exacto de Python, así que el término sale de
    un único redondeo.
    """
    acumulado = 0.0
    for k in range(1, n + 1):
        acumulado = acumulado + 1.0 / (k * (k + 1))
    return acumulado


def b_telescopica(n: int) -> float:
    """b_N sumando los términos 1/k - 1/(k+1).

    Cada término encadena dos divisiones y una resta entre dos números que se
    parecen cada vez más al crecer k.
    """
    acumulado = 0.0
    for k in range(1, n + 1):
        acumulado = acumulado + (1.0 / k - 1.0 / (k + 1))
    return acumulado


def b_cerrada(n: int) -> float:
    """La forma cerrada N/(N+1), con un solo redondeo sobre enteros exactos."""
    return n / (n + 1)


def b_uno_menos(n: int) -> float:
    """BONUS: la forma cerrada escrita como 1 - 1/(N+1), con dos redondeos."""
    return 1.0 - 1.0 / (n + 1)


# --- Las dos representaciones de c_N --------------------------------------------

def termino_cociente(k: int) -> float:
    """El término 1/(sqrt(k^2+1) + k): una suma de números del mismo signo."""
    return 1.0 / (math.sqrt(k * k + 1.0) + k)


def termino_diferencia(k: int) -> float:
    """El término sqrt(k^2+1) - k: una resta entre dos números casi iguales."""
    return math.sqrt(k * k + 1.0) - k


def c_cociente(n: int) -> float:
    """c_N sumando los términos escritos como cociente."""
    acumulado = 0.0
    for k in range(1, n + 1):
        acumulado = acumulado + 1.0 / (math.sqrt(k * k + 1.0) + k)
    return acumulado


def c_diferencia(n: int) -> float:
    """c_N sumando los términos escritos como diferencia de raíces."""
    acumulado = 0.0
    for k in range(1, n + 1):
        acumulado = acumulado + (math.sqrt(k * k + 1.0) - k)
    return acumulado


def error_relativo(aproximacion: float, n: int) -> float:
    """Error relativo de una suma numérica de b_N respecto de la forma cerrada."""
    teorico = b_cerrada(n)
    return abs(aproximacion - teorico) / abs(teorico)


# --- Trazas sobre la grilla de N ------------------------------------------------

def _traza(termino, enes: tuple) -> list:
    """Sumas parciales de `termino` en cada N de la grilla, en un único barrido."""
    valores, acumulado, siguiente = [], 0.0, 0
    for k in range(1, enes[-1] + 1):
        acumulado = acumulado + termino(k)
        while siguiente < len(enes) and k == enes[siguiente]:
            valores.append(acumulado)
            siguiente += 1
    return valores


def _verificar_trazas() -> None:
    """Comprueba que las trazas coincidan bit a bit con las cuatro funciones públicas.

    Es la garantía de que el barrido único no cambia el resultado: si alguna vez
    dejara de coincidir, el experimento estaría midiendo otra cosa.
    """
    control = (1, 10, 137, 1000, 4321)
    pares = (
        ("b producto", lambda k: 1.0 / (k * (k + 1)), b_producto),
        ("b telescópica", lambda k: 1.0 / k - 1.0 / (k + 1), b_telescopica),
        ("c cociente", termino_cociente, c_cociente),
        ("c diferencia", termino_diferencia, c_diferencia),
    )
    for nombre, termino, funcion in pares:
        for n, valor in zip(control, _traza(termino, control)):
            if valor != funcion(n):
                raise ValueError(
                    f"La traza de {nombre} difiere de la función en N = {n}: "
                    f"{valor!r} contra {funcion(n)!r}.")


def _series() -> dict:
    """Las cuatro sumas y las magnitudes derivadas sobre la grilla RANGO_N."""
    bp = _traza(lambda k: 1.0 / (k * (k + 1)), RANGO_N)
    bt = _traza(lambda k: 1.0 / k - 1.0 / (k + 1), RANGO_N)
    cc = _traza(termino_cociente, RANGO_N)
    cd = _traza(termino_diferencia, RANGO_N)
    # Cota de D_N: lo que aportarían las discrepancias de los términos si no se
    # compensaran entre sí. Se acumula con el mismo barrido para poder graficarla.
    cota = _traza(lambda k: abs(termino_diferencia(k) - termino_cociente(k)), RANGO_N)
    return {
        "b_producto": np.array(bp),
        "b_telescopica": np.array(bt),
        "error_producto": np.array([error_relativo(v, n) for v, n in zip(bp, RANGO_N)]),
        "error_telescopica": np.array([error_relativo(v, n) for v, n in zip(bt, RANGO_N)]),
        "c_cociente": np.array(cc),
        "c_diferencia": np.array(cd),
        "d_n": np.array([abs(a - b) for a, b in zip(cc, cd)]),
        "cota_d_n": np.array(cota),
    }


# --- BONUS: los términos individuales de c_N ------------------------------------

def discrepancia_relativa(k: int) -> float:
    """Diferencia entre las dos representaciones del término k, relativa al cociente.

    El cociente no cancela, así que se lo toma como referencia. La cota teórica
    de esta cantidad es 2 k^2 u.
    """
    cociente = termino_cociente(k)
    return abs(termino_diferencia(k) - cociente) / cociente


def _primeros_cruces() -> dict:
    """Primer k, escaneando de a uno, donde la discrepancia relativa alcanza cada umbral."""
    cruces: dict = {}
    for k in range(1, K_FINO + 1):
        if len(cruces) == len(UMBRALES):
            break
        discrepancia = discrepancia_relativa(k)
        for umbral in UMBRALES:
            if umbral not in cruces and discrepancia >= umbral:
                cruces[umbral] = (k, discrepancia)
    faltantes = [u for u in UMBRALES if u not in cruces]
    if faltantes:
        raise ValueError(
            f"Los umbrales {faltantes} no se alcanzan con k <= {K_FINO}: "
            "hay que ampliar K_FINO o sacarlos de UMBRALES.")
    return cruces


def primer_k_colapso(limite_exponente: int = 40) -> int:
    """Primer k donde sqrt(k^2+1) devuelve exactamente k y la resta da cero.

    Dentro de una binada (los k entre dos potencias de dos consecutivas) el
    espaciado de los flotantes es constante y la separación real entre
    sqrt(k^2+1) y k, que vale 1/(2k), decrece. La condición es entonces monótona
    en k dentro de la binada: se busca la primera binada donde se cumple al
    final y se biseca dentro de ella.
    """
    for exponente in range(0, limite_exponente):
        fin = 2 ** (exponente + 1) - 1
        if termino_diferencia(fin) != 0.0:
            continue
        bajo, alto = 2 ** exponente, fin
        while bajo < alto:
            medio = (bajo + alto) // 2
            if termino_diferencia(medio) == 0.0:
                alto = medio
            else:
                bajo = medio + 1
        return bajo
    raise ValueError(f"No hay colapso con k < 2^{limite_exponente}.")


def _k_predicho(umbral: float) -> int:
    """El k donde la cota 2 k^2 u alcanza el umbral."""
    return math.ceil(math.sqrt(umbral / (2.0 * U)))


# --- BONUS: las dos formas cerradas de b_N --------------------------------------

def _discrepancias_cerradas(enes) -> list:
    """Los N de `enes` donde 1 - 1/(N+1) y N/(N+1) no dan el mismo flotante."""
    return [n for n in enes if b_uno_menos(n) != b_cerrada(n)]


def _primer_n_saturado(forma) -> int:
    """Primer N donde `forma` devuelve exactamente 1.0.

    Las dos formas crecen con N, así que una vez que redondean a uno se quedan
    ahí y la búsqueda se puede bisecar.
    """
    bajo, alto = 1, 2 ** 60
    while bajo < alto:
        medio = (bajo + alto) // 2
        if forma(medio) == 1.0:
            alto = medio
        else:
            bajo = medio + 1
    return bajo


def _error_exacto(valor: float, n: int) -> float:
    """Error relativo de `valor` contra el racional exacto N/(N+1).

    Las dos formas cerradas se comparan contra la fracción y no contra un
    flotante de referencia, porque acá lo que se mide es justamente el redondeo
    de esas dos expresiones.
    """
    exacto = Fraction(n, n + 1)
    return float(abs(Fraction(valor) - exacto) / exacto)


def _peores_errores_cerradas() -> dict:
    """Error relativo máximo de cada forma cerrada contra el racional exacto."""
    peores = {"1 - 1/(N+1)": (0.0, 0), "N/(N+1)": (0.0, 0)}
    for n in range(1, N_ERROR_CERRADAS + 1):
        for nombre, forma in (("1 - 1/(N+1)", b_uno_menos), ("N/(N+1)", b_cerrada)):
            error = _error_exacto(forma(n), n)
            if error > peores[nombre][0]:
                peores[nombre] = (error, n)
    return peores


# --- Figuras --------------------------------------------------------------------

def _figura_bn(series: dict) -> None:
    """Error relativo de las dos representaciones de b_N contra la forma cerrada."""
    fig, eje = plt.subplots(figsize=(7.4, 4.6))
    x = np.asarray(RANGO_N, dtype=float)
    # El de producto se dibuja primero y con marcador más grande: los dos caen
    # sobre la misma banda de valores y si no uno taparía al otro.
    eje.plot(x, series["error_producto"], ".", ms=4.5, alpha=0.75,
             color=COLOR_ESTABLE, zorder=2)
    eje.plot(x, series["error_telescopica"], ".", ms=2.6, alpha=0.85,
             color=COLOR_SUSCEPTIBLE, zorder=3)
    eje.plot(x, np.sqrt(x) * U, color=COLOR_COTA, ls="--", lw=1.3, zorder=4)
    eje.axhline(U, color="0.55", ls=":", lw=1.3, zorder=4)
    eje.set_xscale("log")
    # symlog: las dos representaciones dan error exactamente nulo en decenas de
    # N, y en escala logarítmica esos puntos desaparecerían del gráfico.
    eje.set_yscale("symlog", linthresh=1e-16, linscale=0.6)
    # El error relativo no es negativo: sin este límite, symlog reserva media
    # figura para una banda vacía debajo del cero.
    eje.set_ylim(bottom=0.0)
    eje.set_xlabel("$N$ (cantidad de términos)")
    eje.set_ylabel("error relativo")

    entradas = [
        (Line2D([], [], color=COLOR_ESTABLE, ls="none", marker="o", ms=5),
         r"$\sum 1/(k(k+1))$"),
        (Line2D([], [], color=COLOR_SUSCEPTIBLE, ls="none", marker="o", ms=5),
         r"$\sum \left(1/k - 1/(k+1)\right)$"),
        (Line2D([], [], color=COLOR_COTA, ls="--", lw=1.3), r"$\sqrt{N}\,u$"),
        (Line2D([], [], color="0.55", ls=":", lw=1.3), r"$u = 2^{-53}$"),
    ]
    handles, etiquetas = zip(*entradas)
    fig.legend(handles, etiquetas, loc="lower center", ncol=2,
               bbox_to_anchor=(0.5, -0.13))
    fig.tight_layout()
    comun.guardar_figura(fig, "exp3-representaciones-bn")


def _figura_cn(series: dict, k_colapso: int) -> None:
    """La cancelación de c_N vista de dos maneras: acumulada en D_N y término a término."""
    fig, (arriba, abajo) = plt.subplots(2, 1, figsize=(7.4, 7.0))

    x = np.asarray(RANGO_N, dtype=float)
    arriba.plot(x, series["d_n"], ".", ms=3.2, color=COLOR_SUSCEPTIBLE, zorder=3)
    arriba.plot(x, series["cota_d_n"], color=COLOR_COTA, ls="--", lw=1.3, zorder=2)
    arriba.plot(x, x * x * U, color="0.55", ls=":", lw=1.3, zorder=2)
    arriba.set_xscale("log")
    arriba.set_yscale("log")
    arriba.set_xlabel("$N$ (cantidad de términos)")
    arriba.set_ylabel("$D_N$")
    arriba.set_title(r"(a) diferencia entre las dos representaciones de $c_N$")
    arriba.legend(
        handles=[
            Line2D([], [], color=COLOR_SUSCEPTIBLE, ls="none", marker="o", ms=5),
            Line2D([], [], color=COLOR_COTA, ls="--", lw=1.3),
            Line2D([], [], color="0.55", ls=":", lw=1.3),
        ],
        labels=[r"$D_N = |c_N^{(1)} - c_N^{(2)}|$",
                r"$\sum_{k \leq N} |c_k^{(2)} - c_k^{(1)}|$ (sin compensación)",
                r"$N^{2} u$"],
        loc="upper left")

    ks = np.unique(np.geomspace(1, K_MAXIMO, 500).astype(np.int64))
    discrepancias = np.array([discrepancia_relativa(int(k)) for k in ks])
    abajo.plot(ks, discrepancias, ".", ms=3.6, color=COLOR_SUSCEPTIBLE, zorder=3)
    abajo.plot(ks, 2.0 * ks.astype(float) ** 2 * U, color=COLOR_COTA,
               ls="--", lw=1.3, zorder=2)
    abajo.axvline(k_colapso, color="0.45", lw=1.1, zorder=1)
    abajo.annotate(r"$k = 2^{26}$: la resta da $0$", xy=(k_colapso, 2.5e-16),
                   xytext=(-6, 0), textcoords="offset points",
                   ha="right", va="bottom", rotation=90, fontsize=9, color="0.30")
    abajo.set_xscale("log")
    abajo.set_yscale("log")
    abajo.set_ylim(1e-17, 5.0)
    abajo.set_xlabel("$k$ (índice del término)")
    abajo.set_ylabel(r"discrepancia relativa $\delta_k$")
    abajo.set_title(r"(b) las dos representaciones del término $k$")
    abajo.legend(
        handles=[
            Line2D([], [], color=COLOR_SUSCEPTIBLE, ls="none", marker="o", ms=5),
            Line2D([], [], color=COLOR_COTA, ls="--", lw=1.3),
        ],
        labels=[r"$\delta_k = |c_k^{(2)} - c_k^{(1)}| / c_k^{(1)}$", r"$2k^{2}u$"],
        loc="upper left")

    fig.tight_layout()
    comun.guardar_figura(fig, "exp3-cancelacion-cn")


# --- Tablas ---------------------------------------------------------------------

def _tabla_bn(series: dict) -> None:
    """Error relativo de las dos representaciones de b_N en unos pocos N."""
    filas = []
    for n in N_TABLA:
        indice = RANGO_N.index(n)
        producto = series["b_producto"][indice]
        telescopica = series["b_telescopica"][indice]
        separacion = abs(producto - telescopica) / math.ulp(b_cerrada(n))
        filas.append([
            comun.formato_entero(n),
            comun.formato_cientifico(series["error_producto"][indice]),
            comun.formato_cientifico(series["error_telescopica"][indice]),
            f"${separacion:.0f}$",
        ])
    comun.guardar_tabla(
        filas,
        [r"$N$", r"$E_\mathrm{rel}$ de $b_N^{(1)}$", r"$E_\mathrm{rel}$ de $b_N^{(2)}$",
         r"$|b_N^{(1)} - b_N^{(2)}|$ (ulp)"],
        "exp3-bn-representaciones")


def _tabla_resumen(series: dict) -> None:
    """Resumen de las dos sucesiones sobre la grilla completa de N.

    Las tablas de b_N y de c_N muestran cinco valores de N; esta resume los 1001
    de la grilla, que es de donde salen las afirmaciones del informe sobre el
    máximo, sobre cuántos N dan error nulo y sobre cuántos hacen coincidir bit a
    bit las dos representaciones.
    """
    total = len(RANGO_N)
    coinciden = int(np.count_nonzero(series["b_producto"] == series["b_telescopica"]))
    nulos_dn = int(np.count_nonzero(series["d_n"] == 0))
    filas = [
        [r"$E_\mathrm{rel}$ máximo de $b_N^{(1)}$",
         comun.formato_cientifico(series["error_producto"].max())],
        [r"$E_\mathrm{rel}$ máximo de $b_N^{(2)}$",
         comun.formato_cientifico(series["error_telescopica"].max())],
        [r"$N$ con $E_\mathrm{rel} = 0$ en $b_N^{(1)}$",
         f"${int(np.count_nonzero(series['error_producto'] == 0))}$ de ${total}$"],
        [r"$N$ con $E_\mathrm{rel} = 0$ en $b_N^{(2)}$",
         f"${int(np.count_nonzero(series['error_telescopica'] == 0))}$ de ${total}$"],
        [r"$N$ con $b_N^{(1)} = b_N^{(2)}$", f"${coinciden}$ de ${total}$"],
        [r"$N$ con $D_N = 0$", f"${nulos_dn}$ de ${total}$"],
    ]
    comun.guardar_tabla(filas, ["magnitud", "valor"], "exp3-resumen",
                        alineacion="lr")


def _tabla_cn(series: dict) -> None:
    """D_N y las cifras significativas que comparten las dos representaciones de c_N."""
    filas = []
    for n in N_TABLA:
        indice = RANGO_N.index(n)
        cociente = series["c_cociente"][indice]
        d_n = series["d_n"][indice]
        relativa = d_n / cociente
        cifras = math.floor(-math.log10(relativa)) if d_n > 0 else 17
        filas.append([
            comun.formato_entero(n),
            f"${cociente:.12f}$",
            comun.formato_cientifico(d_n),
            comun.formato_cientifico(relativa),
            f"${cifras}$",
        ])
    comun.guardar_tabla(
        filas,
        [r"$N$", r"$c_N^{(1)}$", r"$D_N$", r"$D_N/c_N^{(1)}$",
         "cifras coincidentes"],
        "exp3-cn-diferencia")


def _tabla_bonus_terminos(cruces: dict, k_colapso: int) -> None:
    """BONUS: a partir de qué k la pérdida de precisión del término alcanza cada nivel."""
    filas = []
    for umbral in UMBRALES:
        k, discrepancia = cruces[umbral]
        filas.append([
            comun.formato_cientifico(umbral, decimales=0),
            comun.formato_entero(_k_predicho(umbral)),
            comun.formato_entero(k),
            comun.formato_cientifico(discrepancia),
        ])
    filas.append([
        "$1$",
        comun.formato_entero(_k_predicho(1.0)),
        comun.formato_entero(k_colapso),
        "$1$",
    ])
    comun.guardar_tabla(
        filas,
        [r"$\varepsilon$", r"$k$ que predice $2k^{2}u$",
         r"primer $k$ con $\delta_k \ge \varepsilon$", r"$\delta_k$ en ese $k$"],
        "exp3-bonus-terminos")


def _tabla_bonus_cerradas(discrepancias_grilla: list, discrepancias_rango: list,
                          peores: dict, saturacion: dict) -> None:
    """BONUS: en qué se diferencian 1 - 1/(N+1) y N/(N+1)."""
    if not discrepancias_grilla:
        cuales = "ninguno"
    elif len(discrepancias_grilla) <= 5:
        cuales = ", ".join(comun.formato_entero(n) for n in discrepancias_grilla)
    else:
        cuales = ", ".join(comun.formato_entero(n)
                           for n in discrepancias_grilla[:5]) + r", \ldots"
    separaciones = {abs(b_uno_menos(n) - b_cerrada(n)) / math.ulp(b_cerrada(n))
                    for n in discrepancias_rango}
    filas = [
        [r"$N$ de la grilla donde difieren",
         f"${len(discrepancias_grilla)}$ de ${len(RANGO_N)}$"],
        [r"cuáles son esos $N$", cuales],
        [f"$N <$ {comun.formato_entero(N_CONTEO_CERRADAS)} donde difieren",
         f"${len(discrepancias_rango)}$ de {comun.formato_entero(N_CONTEO_CERRADAS - 1)}"],
        ["separación cuando difieren",
         " y ".join(f"${s:.0f}$ ulp" for s in sorted(separaciones))],
        [r"$E_\mathrm{rel}$ máximo de $1 - 1/(N+1)$",
         comun.formato_cientifico(peores["1 - 1/(N+1)"][0])],
        [r"$E_\mathrm{rel}$ máximo de $N/(N+1)$",
         comun.formato_cientifico(peores["N/(N+1)"][0])],
        [r"primer $N$ con $1 - 1/(N+1) = 1$",
         comun.formato_entero(saturacion["1 - 1/(N+1)"])],
        [r"primer $N$ con $N/(N+1) = 1$",
         comun.formato_entero(saturacion["N/(N+1)"])],
    ]
    comun.guardar_tabla(filas, ["magnitud", "valor"], "exp3-bonus-formas-cerradas",
                        alineacion="lr")


# --- Punto de entrada -----------------------------------------------------------

def correr() -> None:
    """Genera las figuras y tablas del experimento 3 e imprime un resumen corto."""
    _verificar_trazas()
    series = _series()
    cruces = _primeros_cruces()
    k_colapso = primer_k_colapso()
    discrepancias_grilla = _discrepancias_cerradas(RANGO_N)
    discrepancias_rango = _discrepancias_cerradas(range(1, N_CONTEO_CERRADAS))
    peores = _peores_errores_cerradas()
    saturacion = {"1 - 1/(N+1)": _primer_n_saturado(b_uno_menos),
                  "N/(N+1)": _primer_n_saturado(b_cerrada)}

    _figura_bn(series)
    _figura_cn(series, k_colapso)
    _tabla_bn(series)
    _tabla_resumen(series)
    _tabla_cn(series)
    _tabla_bonus_terminos(cruces, k_colapso)
    _tabla_bonus_cerradas(discrepancias_grilla, discrepancias_rango, peores, saturacion)

    coinciden_bn = int(np.count_nonzero(series["b_producto"] == series["b_telescopica"]))
    print("[experimento 3] representaciones de una suma")
    for nombre, clave in (("producto", "error_producto"),
                          ("telescópica", "error_telescopica")):
        errores = series[clave]
        print(f"  b_N {nombre:>12}: error máximo {errores.max():.2e}, "
              f"{int(np.count_nonzero(errores == 0))} de {len(errores)} exactos")
    print(f"  las dos representaciones de b_N coinciden en {coinciden_bn} "
          f"de {len(RANGO_N)} valores de N")
    d_n = series["d_n"]
    print(f"  c_N: D_N crece de {d_n[0]:.2e} (N = {RANGO_N[0]}) a "
          f"{d_n[-1]:.2e} (N = {RANGO_N[-1]}); "
          f"nula en {int(np.count_nonzero(d_n == 0))} de {len(d_n)} valores de N")
    print(f"  términos: la discrepancia relativa pasa 1e-8 en k = {cruces[1e-8][0]} "
          f"y llega a 1 en k = {k_colapso}")
    separaciones = sorted({abs(b_uno_menos(n) - b_cerrada(n)) / math.ulp(b_cerrada(n))
                           for n in discrepancias_rango})
    print(f"  formas cerradas: difieren en {len(discrepancias_rango)} de "
          f"{N_CONTEO_CERRADAS - 1} valores de N, por "
          f"{' y '.join(f'{s:.0f}' for s in separaciones)} ulp")
    print("  2 figuras y 5 tablas escritas en informe/figuras y informe/tablas")
