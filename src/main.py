"""Punto de entrada: corre los tres experimentos y regenera figuras y tablas del informe.

Uso:
    python src/main.py        # los tres experimentos
    python src/main.py 2      # solo el experimento 2
"""
import sys

# La consola de Windows suele abrirse en cp1252 y rompe las tildes del resumen.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import experimento1_asociativa
import experimento2_conmutativa
import experimento3_representaciones

EXPERIMENTOS = {
    1: experimento1_asociativa,
    2: experimento2_conmutativa,
    3: experimento3_representaciones,
}


def main(argv: list[str]) -> None:
    """Corre los experimentos que se pidan por línea de comandos, o los tres.

    Cada experimento regenera sus figuras en `informe/figuras/` y sus tablas en
    `informe/tablas/`, e imprime un resumen corto de control en la consola.
    """
    elegidos = [int(a) for a in argv] if argv else sorted(EXPERIMENTOS)
    for numero in elegidos:
        if numero not in EXPERIMENTOS:
            raise SystemExit(f"Experimento inválido: {numero}. Opciones: 1, 2, 3.")
        EXPERIMENTOS[numero].correr()


if __name__ == "__main__":
    main(sys.argv[1:])
