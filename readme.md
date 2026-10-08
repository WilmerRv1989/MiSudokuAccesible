# MiSudokuAccesible

*Sudoku accesible para NVDA, para todas las edades.*

Hola, soy Wilmer. Siempre quise jugar al sudoku: es una forma estupenda de ejercitar la concentración y la atención, unos minutos cada día. Pero nunca encontré un sudoku que fuera de verdad cómodo con un lector de pantalla, así que decidí hacer el mío.

MiSudokuAccesible es el segundo juego de mi colección para NVDA, después de [MiAjedrezAccesible](https://github.com/WilmerRv1989/MiAjedrezAccesible). Lo hice pensando en dos tipos de jugadores: cualquier persona que quiera un buen sudoku con NVDA, y niñas y niños que están empezando a aprender. Por eso no solo deja jugar: te enseña a pensar cada jugada.

* Manual completo: [addon/doc/es/readme.md](addon/doc/es/readme.md).
* English version: [readme_en.md](readme_en.md).

## Qué vas a encontrar

* **Sudokus de 9 por 9** en tres niveles. Cada nivel se mide por las técnicas que necesitas para resolverlo, no solo por cuántos números vienen puestos, así que «Difícil» es difícil de verdad.
* **Mini sudokus de 4 por 4 y 6 por 6**, ideales para empezar y para niñas y niños.
* **Pistas que enseñan.** Pulsa P y te digo dónde mirar; pulsa Mayúsculas+P y te explico qué número va, dónde y por qué. Las pistas nunca escriben el número por ti: encontrarlo es lo divertido.
* **Con o sin ayudas.** Cuando te sientas preparado, juega sin pistas ni aviso de choques, como en papel.
* **Aprender a jugar**, un curso guiado de 13 lecciones: desde las reglas y cómo moverse por el tablero hasta las intersecciones y las parejas, con práctica sin fin de cada técnica.
* **El sudoku del día**, el mismo para todas las personas, para crear el hábito y sumar días seguidos.
* **Mis estadísticas**, un panel de opciones y una lista de atajos de teclado.

Cada casilla se lee por voz y en braille, y todo se guarda solo: cierra el tablero, o incluso NVDA, y sigue después donde lo dejaste. El complemento funciona con NVDA 2026.1 o posterior, no necesita Internet y no envía ningún dato.

## Por dónde empezar

Todo se abre desde el menú de NVDA (NVDA+N), Herramientas, MiSudokuAccesible:

* Si nunca has jugado al sudoku, empieza por **Aprender a jugar**, desde la lección 1. Tómate tu tiempo.
* Si ya sabes jugar, elige **Nuevo sudoku** o prueba el **Sudoku del día**.
* Si te atascas, pulsa **P**. Para eso están las pistas.

## Teclas del tablero

| Tecla | Acción |
|---|---|
| Flechas | Moverse por las casillas |
| Inicio / Fin | Primera o última casilla de la fila |
| Tab / Mayúsculas+Tab | Siguiente o anterior casilla vacía |
| 1 a 9 | Escribir ese número |
| Mayúsculas+1 a 9 | Poner o quitar ese número como nota |
| Suprimir o Retroceso | Borrar el número de la casilla o, si no tiene, sus notas |
| Control+Z | Deshacer el último cambio |
| P | Pista breve: dónde mirar y qué buscar |
| Mayúsculas+P | Pista completa: qué número va, dónde y por qué |
| N | Leer las notas de la casilla |
| F / C / B | Leer la fila, la columna o el bloque: qué números tiene y cuáles faltan |
| F5 | Cuántas casillas faltan |
| Aplicaciones o Mayúsculas+F10 | Menú del tablero |
| Escape | Cerrar el tablero (el sudoku se guarda) |

Los bloques se numeran de izquierda a derecha y de arriba abajo. Puedes cambiar cualquier tecla en los Gestos de entrada de NVDA, categoría MiSudokuAccesible.

## Cómo lo hice

Desarrollé MiSudokuAccesible con la asistencia de Claude, un modelo de inteligencia artificial de Anthropic. Claude escribió la mayor parte del código siguiendo mis indicaciones, consultó la documentación y el código de NVDA y me propuso soluciones técnicas. La dirección y las decisiones fueron mías: el diseño del complemento, el curso y la forma de enseñar, los sonidos, cómo se comporta con el lector de pantalla y qué dejar fuera.

Probé y aprobé yo mismo con NVDA cada versión, función, tecla y mensaje de voz. Te lo cuento porque creo que es lo honesto. Si encuentras un error, la responsabilidad es mía, y me ayudas mucho si me lo haces saber.

## Escríbeme

Si algo no funciona, si tienes una idea o simplemente quieres contarme qué tal te fue, escríbeme a contacto@wilmer-rv.com o abre un [reporte en GitHub](https://github.com/WilmerRv1989/MiSudokuAccesible/issues). Lo leo todo.

Hecho con amor por Wilmer Rodríguez Vega ([wilmer-rv.com](https://wilmer-rv.com)).

Con licencia GPL de GNU, versión 2 o posterior.
