# Informe: Implementación de Sumatorias

Cálculo Aplicado, UCU, segundo semestre 2026.
Autores: Martín De León, Manuel Chouhy, Joaquín Riál.

Estudio experimental de tres fenómenos de la aritmética de punto flotante usando sumatorias:
pérdida de la asociatividad, dependencia del orden de suma (con suma de Kahan) y diferencias
entre representaciones matemáticamente equivalentes (cancelación catastrófica).

## Estructura

```
src/       código Python: un módulo por experimento, comun.py y main.py
informe/   LaTeX: main.tex, secciones/, figuras/ y tablas/ generadas por el código
docs/      REQUISITOS.md: requisitos de la consigna
```

## Requisitos

Python 3.12 o superior.

```
pip install -r requirements.txt
```

## Uso

```
python src/main.py      # corre los tres experimentos y regenera figuras y tablas (unos 3 minutos)
python src/main.py 1    # solo el experimento 1
```

El informe se compila desde `informe/main.tex` con cualquier distribución de LaTeX o en Overleaf.
