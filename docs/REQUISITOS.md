# Requisitos del trabajo

Destilado de tres fuentes: la consigna (`material/Calculo_Aplicado___Implementacion_de_Sumatorias.pdf`),
la Guía de informe académico (`material/Guia_de_informe_academico (1).pdf`) y la rúbrica
(`material/Rúbricas para informes.xlsx`). Cada línea es verificable. Se usa para revisar antes de entregar.

## 1. Qué pide la consigna

### Experimento 1: propiedad asociativa

Sucesión `a_N = Σ_{k=1}^{N} (1 + b^k − b^k) = N`.

- [ ] Función que recibe N y b y devuelve la suma para las tres asociaciones:
      `(1 + b^k − b^k)`, `(1 + b^k) − b^k`, `(1 − b^k) + b^k`. Sin `sum()`.
- [ ] Figura: a_N para N = 1..1000, las tres asociaciones, b ∈ {2, 3, 5, 10} de tipo `int`.
- [ ] Figura: ídem con b ∈ {2.0, 3.0, 5.0, 10.0} de tipo `float`.
- [ ] Responder: qué diferencias hay entre int y float y por qué (enteros de precisión
      arbitraria vs. IEEE 754 con 53 bits de mantisa; pérdida del 1 cuando b^k > 2^53;
      desborde a inf y NaN).
- [ ] BONUS: ¿con b ≤ 1 se observa el fenómeno?
- [ ] BONUS: ¿hay situaciones donde b entero y números grandes den problemas? Responder en
      general (enteros de tamaño fijo, overflow en C/Java) y en Python (big ints, costo en tiempo
      y memoria).
- [ ] BONUS: repetir con b negativo y describir qué se observa.

### Experimento 2: propiedad conmutativa

Sucesión `b_N = Σ_{k=1}^{N} 1/(k(k+1)) = N/(N+1)`.

- [ ] Cuatro algoritmos de suma que reciben solo N, sin `sum()`: mayor a menor módulo,
      menor a mayor módulo, randomizada, Kahan.
- [ ] Error relativo `|b_num − b_teórico| / |b_teórico|` para cada algoritmo.
- [ ] Figura: error relativo vs N para N = 10, 20, ..., 10000, los cuatro algoritmos, con
      escala que permita ver las diferencias (logarítmica en el eje y).
- [ ] Figura: ídem para N = 1000, 2000, ..., 1 000 000, y comparación con el rango anterior.
- [ ] Suma randomizada repetida varias veces para un N grande: ¿da siempre lo mismo?, ¿cómo
      varía el error relativo entre ejecuciones? (tabla o figura con la dispersión).
- [ ] Marco teórico: qué es la suma de Kahan, con referencia.

### Experimento 3: representaciones de una suma

`b_N = Σ 1/(k(k+1)) = Σ (1/k − 1/(k+1)) = N/(N+1)` y
`c_N = Σ 1/(√(k²+1) + k) = Σ (√(k²+1) − k)`.

- [ ] Funciones para las dos representaciones de b_N y las dos de c_N. Solo reciben N. Sin `sum()`.
- [ ] Figura: error relativo de cada representación de b_N contra la forma cerrada, para
      N = 1, 10, 20, ..., 10000. Responder si dan lo mismo y cómo evoluciona el error.
- [ ] Figura: `D_N = |c_N^(1) − c_N^(2)|` vs N. Responder si son idénticas y qué explica la diferencia.
- [ ] Marco teórico y Discusión: cancelación catastrófica, con referencia, y por qué
      `√(k²+1) − k` es la representación susceptible.
- [ ] BONUS: `1 − 1/(N+1)` vs `N/(N+1)`: implementar ambas y estudiar si son numéricamente
      equivalentes al crecer N.
- [ ] BONUS: términos individuales `√(k²+1) − k` vs `1/(√(k²+1) + k)`: cómo varía la
      diferencia con k y a partir de qué k se aprecia la pérdida de precisión.

## 2. Qué pide la guía de informe

Estructura obligatoria, en este orden:

- [ ] **Portada**: título descriptivo del problema, nombres de los tres autores, fecha, curso,
      docentes, universidad.
- [ ] **Resumen**: objetivo, metodología, resultados más relevantes, conclusión principal.
      Máximo 300 palabras. Autosuficiente.
- [ ] **Índice** (el informe de referencia lo incluye).
- [ ] **Introducción**: planteo del problema, justificación, objetivos generales y
      específicos, estructura del informe. Más larga que el resumen.
- [ ] **Marco teórico**: una subsección por concepto clave, solo los que se usan:
      representación en punto flotante (IEEE 754, épsilon de máquina, redondeo), enteros de
      precisión arbitraria en Python, asociatividad y conmutatividad en punto flotante,
      error relativo, suma de Kahan, cancelación catastrófica, sumas telescópicas.
- [ ] **Metodología**: herramientas (Python, NumPy, Matplotlib, versiones), diseño de cada
      experimento, criterios de análisis, semilla, **link al repositorio** (solo acá).
- [ ] **Resultados**: datos, figuras y tablas sin interpretación. Organizado por fenómeno,
      no por ítem de la consigna.
- [ ] **Discusión**: interpretación, comparación con la teoría, hallazgos inesperados,
      limitaciones.
- [ ] **Conclusiones**: síntesis, respuesta a los objetivos, recomendaciones, líneas futuras.
      Sin resultados nuevos.
- [ ] **Bibliografía**: todas las fuentes citadas, formato APA, y todas usadas en el cuerpo.
- [ ] Anexo: opcional; no poner ahí nada esencial.

Figuras:
- [ ] Numeradas correlativamente, pie de figura debajo, ejes identificados con unidades,
      leyenda que no tape las curvas, autocontenidas.
- [ ] Citadas en el texto por número ("como se observa en la Figura 2").
- [ ] Tamaño legible; nada de figuras chicas ni capturas de pantalla.

Tablas:
- [ ] Numeradas, título encima con unidades, notas debajo, autocontenidas, citadas por número.
- [ ] Generadas desde el código, nunca capturas de consola.

## 3. Qué mira la rúbrica

Tres dimensiones con nota propia: **fondo** (contenido), **forma** (comunicación) y **código**.
Nota final 1.0 requiere al menos dos dimensiones en Excelente (sin errores, pocas imperfecciones).

Errores graves que hunden todo el trabajo:
- [ ] No estructurado como entrega de ejercicios.
- [ ] Ninguna parte de la consigna sin hacer o sin analizar.
- [ ] Sin errores conceptuales ni terminología mal usada de forma persistente.
- [ ] Simbología matemática cuidada (todo en modo matemático de LaTeX).
- [ ] Un solo informe, en PDF.
- [ ] Sin fotos de cuaderno.
- [ ] Portada según lo pedido.
- [ ] El código corre, se reproduce y hace lo que el informe dice.

Errores graves localizados:
- [ ] Toda afirmación fuerte apoyada en datos, figuras o referencias.
- [ ] Nada prometido en la introducción que después no aparezca.
- [ ] Metodología suficiente para reproducir.
- [ ] Todos los datos pedidos presentes; ninguno que el código no genere.
- [ ] Conclusiones que se siguen de los datos.
- [ ] Sin prints voluminosos; imports completos; semillas bien usadas.

Errores leves (en naranja en la rúbrica: comprometen la calidad):
- [ ] Ortografía y sintaxis cuidadas; sin errores de tipeo persistentes.
- [ ] Sin terminología rebuscada fuera del alcance del curso sin explicar.
- [ ] Sin capturas de consola como tablas; figuras legibles y estéticas.
- [ ] Cada sección con todas sus partes (la introducción explica objetivos y estructura).
- [ ] Citas APA correctas.
- [ ] Código comentado y ordenado; ni un archivo por ítem ni todo en uno.

Imperfecciones (no son errores, pero suman o restan):
- [ ] No llamar "ejercicio" al trabajo.
- [ ] Citar el propio trabajo cuando ayuda ("como se mostró en la sección 2.3").
- [ ] Justificar las decisiones metodológicas (por qué escala log, por qué esa semilla).
- [ ] Hacer algo más de lo pedido (los BONUS, una figura extra que ayude).
- [ ] Comentarios en el código; sin prints innecesarios; vectorizar cuando aplica sin violar la
      prohibición de `sum()`.
