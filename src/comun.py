"""Utilidades compartidas por los tres experimentos.

Semilla, rutas de salida y helpers para guardar figuras y tablas en el formato
que espera el informe LaTeX. Ningún módulo de experimento escribe archivos por su cuenta.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # sin ventana: solo se guardan archivos
import matplotlib.pyplot as plt
import numpy as np

SEMILLA_MAESTRA = 20260908  # única semilla del trabajo; todo lo aleatorio deriva de acá

RAIZ = Path(__file__).resolve().parent.parent
DIR_FIGURAS = RAIZ / "informe" / "figuras"
DIR_TABLAS = RAIZ / "informe" / "tablas"


def generador(*claves: int) -> np.random.Generator:
    """Generador reproducible e independiente para la corrida identificada por `claves`.

    Cada corrida aleatoria recibe un generador distinto, derivado de la semilla
    maestra, para que las repeticiones sean independientes entre sí pero
    reproducibles. Las claves identifican la corrida: por convención, el número
    de experimento seguido de lo que distinga a esa corrida dentro del
    experimento (el valor de N, el número de repetición). Dos corridas con
    claves distintas nunca comparten el estado inicial del generador.
    """
    return np.random.default_rng([SEMILLA_MAESTRA, *claves])


def aplicar_estilo() -> None:
    """Fija el estilo de todas las figuras del informe.

    Se llama una sola vez al importar el módulo, para que las figuras de los
    tres experimentos salgan con los mismos tamaños y sean legibles impresas.
    """
    plt.rcParams.update({
        "savefig.dpi": 300,
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linewidth": 0.5,
        "lines.linewidth": 1.8,
        "legend.frameon": False,
    })


def guardar_figura(fig: plt.Figure, nombre: str) -> Path:
    """Guarda la figura en informe/figuras/<nombre>.pdf y cierra la figura."""
    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)
    ruta = DIR_FIGURAS / f"{nombre}.pdf"
    fig.savefig(ruta, bbox_inches="tight")
    plt.close(fig)
    return ruta


def guardar_tabla(filas: list[list], encabezados: list[str], nombre: str,
                  alineacion: str | None = None) -> Path:
    """Guarda una tabla como cuerpo de tabular LaTeX en informe/tablas/<nombre>.tex.

    El archivo contiene solo el entorno tabular (con reglas de booktabs), para
    incluirlo con el comando input dentro de un entorno table del informe, que
    es el que aporta el título, la numeración y las notas al pie.

    Los literales de LaTeX se escriben como cadenas crudas: sin la r inicial,
    secuencias como la de begin o la de toprule se convierten en caracteres de
    control y el archivo sale corrupto. La verificación final lo impide.
    """
    DIR_TABLAS.mkdir(parents=True, exist_ok=True)
    ruta = DIR_TABLAS / f"{nombre}.tex"
    cols = alineacion if alineacion else "l" + "r" * (len(encabezados) - 1)
    lineas = [r"\begin{tabular}{" + cols + "}", r"\toprule",
              " & ".join(encabezados) + r" \\", r"\midrule"]
    for fila in filas:
        lineas.append(" & ".join(str(c) for c in fila) + r" \\")
    lineas += [r"\bottomrule", r"\end{tabular}"]
    contenido = "\n".join(lineas) + "\n"
    sospechosos = {c for c in contenido if ord(c) < 32 and c != "\n"}
    if sospechosos:
        raise ValueError(
            f"La tabla {nombre} contiene caracteres de control "
            f"{sorted(hex(ord(c)) for c in sospechosos)}: falta una cadena cruda.")
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def formato_entero(n: int) -> str:
    """Devuelve n en modo matemático con espacio fino cada tres cifras.

    Un número como 1000000 es ilegible dentro de una tabla; el separador fino
    de LaTeX lo agrupa sin introducir puntos ni comas, que ya tienen otro uso
    en el informe.
    """
    grupos = []
    texto = str(abs(n))
    while texto:
        grupos.append(texto[-3:])
        texto = texto[:-3]
    signo = "-" if n < 0 else ""
    return "$" + signo + r"\,".join(reversed(grupos)) + "$"


def formato_cientifico(x: float, decimales: int = 2) -> str:
    """Devuelve x en notación científica lista para modo matemático de LaTeX."""
    if x != x:
        return r"$\mathrm{NaN}$"
    if x in (float("inf"), float("-inf")):
        return r"$\infty$" if x > 0 else r"$-\infty$"
    if x == 0:
        return "$0$"
    texto = f"{x:.{decimales}e}"
    mantisa, exponente = texto.split("e")
    return f"${mantisa} \\times 10^{{{int(exponente)}}}$"


aplicar_estilo()
