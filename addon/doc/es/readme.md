# MiSudokuAccesible

Sudoku accesible para el lector de pantalla NVDA, para todas las edades.

MiSudokuAccesible permite a personas ciegas o con baja visión jugar al sudoku con cada casilla del tablero legible por voz y en braille, y aprender a resolverlo con un curso guiado y con pistas que explican cada jugada. Está pensado también para niñas y niños.

Funciona con NVDA 2026.1 o posterior. No necesita Internet y no envía ningún dato: tu progreso se guarda solo en tu equipo.

## Por dónde empezar

Todo se abre desde el menú de NVDA (NVDA+N), Herramientas, MiSudokuAccesible:

* Si nunca has jugado al sudoku, empieza por **Aprender a jugar**, desde la lección 1.
* Si ya sabes jugar, elige **Nuevo sudoku** o prueba el **Sudoku del día**.
* Si te atascas en un sudoku, pulsa **P** para una pista.

El submenú tiene:

* **Nuevo sudoku...:** elegir tamaño, nivel y ayudas, y empezar.
* **Continuar el sudoku:** solo aparece si tienes uno sin terminar.
* **Sudoku del día:** uno nuevo cada día.
* **Aprender a jugar...:** el curso guiado.
* **Mis estadísticas...:** sudokus resueltos, tiempos, días seguidos y progreso en el curso.
* **Atajos de teclado...:** la lista de todas las teclas.

## Cómo se juega

El tablero tiene 9 filas y 9 columnas, divididas en 9 bloques de 3 por 3. Hay que llenarlo de modo que cada fila, cada columna y cada bloque tenga los números del 1 al 9, sin repetir ninguno. Algunos números vienen puestos desde el principio: son fijos y no se pueden cambiar.

Las filas van de arriba abajo y las columnas de izquierda a derecha. Los bloques se numeran como se lee: de izquierda a derecha y de arriba abajo. El bloque 1 está arriba a la izquierda, el 5 en el centro y el 9 abajo a la derecha.

### Mini sudokus

Para empezar, o para niñas y niños, hay dos tableros más pequeños que se juegan igual:

* **4 por 4:** números del 1 al 4, en 4 bloques de 2 por 2.
* **6 por 6:** números del 1 al 6, en 6 bloques de 2 filas por 3 columnas. Hay dos bloques en cada franja de dos filas: el 1 y el 2 arriba, el 3 y el 4 en el medio, y el 5 y el 6 abajo.

Si pulsas un número más alto que el tablero, suena el tono de error y se oye, por ejemplo, «En este sudoku los números van del 1 al 4».

## Empezar un sudoku

1. Abre el menú de NVDA con NVDA+N.
2. Ve a Herramientas y luego a MiSudokuAccesible.
3. Elige «Nuevo sudoku...».
4. Elige el tamaño (4 por 4, 6 por 6 o 9 por 9), el nivel y las ayudas, y pulsa Aceptar.

El diálogo recuerda lo último elegido. Cada sudoku se crea en el momento y tiene una sola solución. Un sudoku medio o difícil puede tardar un par de segundos: mientras tanto, se oye «Preparando el sudoku...».

### Niveles

Los niveles se miden por las técnicas que hacen falta para resolver el sudoku (ver «Pistas y técnicas»):

* **Fácil:** se resuelve con las tres primeras técnicas y empieza con al menos 36 números puestos.
* **Medio:** necesita al menos una intersección.
* **Difícil:** necesita al menos una pareja.

En los mini sudokus casi nunca hacen falta las técnicas difíciles, así que solo hay dos niveles: **Fácil**, con más números puestos, y **Medio**, con menos.

### Ayudas

La opción **Ayudas** del diálogo permite elegir el reto:

* **Activadas:** pistas con P y Mayúsculas+P, y aviso cuando un número choca.
* **Desactivadas:** sin pistas ni aviso de choques. Un número que choca se escribe sin avisar, como en papel. Comprobar sigue disponible en el menú del tablero.

Leer filas, columnas y bloques (F, C y B), las notas y F5 funcionan siempre: equivalen a lo que se ve al mirar el papel. Cuando las ayudas están desactivadas, el título de la ventana dice «sin ayudas».

## Lo que se oye

* Casilla con un número fijo: «Fila 3, columna 5: 7, fija».
* Casilla con un número que escribiste: «Fila 3, columna 5: 7».
* Casilla vacía: «Fila 3, columna 5, vacía» y, si tiene notas, «notas 1, 4 y 7».
* Al pasar a otro bloque se añade su número: «bloque 2».

Si prefieres algo más breve, en las opciones puedes elegir la forma corta: «F3C5: 7, fija».

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
| F | Leer la fila: qué números tiene y cuáles faltan |
| C | Leer la columna |
| B | Leer el bloque |
| F5 | Cuántas casillas faltan |
| Aplicaciones o Mayúsculas+F10 | Menú del tablero |
| Escape | Cerrar el tablero (el sudoku se guarda) |

Las teclas se pueden cambiar en el menú de NVDA, Preferencias, Gestos de entrada, categoría MiSudokuAccesible. La lista completa, con tus cambios, está en «Atajos de teclado»: en el menú del tablero, en el de las lecciones y en Herramientas, MiSudokuAccesible.

## Ayudas al jugar

* **Choques:** si escribes un número que ya está en su fila, su columna o su bloque, suena un tono y se oye, por ejemplo, «5, choca con el 5 de la fila». Solo se compara con los números que están a la vista, nunca con la solución.
* **Notas:** al escribir un número, esa nota se quita sola de las casillas de su fila, su columna y su bloque. Se puede desactivar en las opciones.
* **Filas, columnas y bloques completos:** cuando uno tiene todos sus números distintos, suena un sonido corto y se oye, por ejemplo, «Fila 3 completa».
* **Comprobar** (en el menú del tablero): dice cuántas casillas están mal, sin decir cuáles.
* **Al terminar:** suena una melodía y se dice el tiempo que tardaste. El tiempo es solo informativo y cuenta únicamente mientras la ventana del tablero está activa. Si es tu mejor tiempo en ese tamaño y nivel, también se dice.

## Pistas y técnicas

Las pistas no escriben nada: te dicen dónde mirar o qué número va, y por qué, y tú vas a la casilla y lo escribes. Se calculan con el tablero tal como está, aunque no hayas puesto notas.

* **P, pista breve:** por ejemplo, «Mira el bloque 4: hay un número que solo cabe en un lugar».
* **Mayúsculas+P, pista completa:** por ejemplo, «En el bloque 4, el 7 solo cabe en la fila 5, columna 2: las demás casillas vacías ya tienen un 7 en su fila, su columna o su bloque».
* Si hay un número equivocado en el tablero, la pista te dice primero dónde está, porque desde un error no se puede razonar bien.
* Cuando hace falta una intersección o una pareja, el número va en un sitio y la razón está en otro. Por eso la pista breve nombra los dos: «Puedes escribir un número en la fila 3, pero antes hace falta una intersección en el bloque 2». La completa dice primero dónde va el número y después por qué.

Las técnicas, de la más fácil a la más difícil:

1. **Último número:** a una fila, columna o bloque solo le falta un número.
2. **Único lugar:** en una fila, columna o bloque, un número solo cabe en una casilla.
3. **Único número:** en una casilla solo cabe un número, porque los demás ya están en su fila, su columna o su bloque.
4. **Intersección:** en un bloque, un número solo puede ir dentro de una misma fila (o columna). Entonces, en el resto de esa fila no puede ir ese número. También al revés: si en una fila un número solo puede ir dentro de un bloque, no puede ir en el resto del bloque.
5. **Pareja:** dos casillas de una fila, columna o bloque solo admiten los mismos dos números. Entonces esos dos números no pueden ir en ninguna otra casilla del grupo. También al revés: si dos números solo caben en las mismas dos casillas, esas casillas no pueden tener otros números.

## Menú del tablero

Se abre con la tecla Aplicaciones o con Mayúsculas+F10:

* **Nuevo sudoku...:** empieza otro sudoku. Si el actual tiene algo escrito, pide confirmación.
* **Comprobar:** cuántas casillas están mal.
* **Reiniciar:** borra todo lo que escribiste y vuelve al principio, con el tiempo a cero. Pide confirmación y no se puede deshacer.
* **Atajos de teclado:** las teclas de esta ventana.
* **Cerrar el tablero.**

## Guardado automático

Cada cambio se guarda solo. Puedes cerrar el tablero con Escape, o cerrar NVDA, sin perder nada. Para seguir, abre Herramientas, MiSudokuAccesible, «Continuar el sudoku».

## Sudoku del día

Herramientas, MiSudokuAccesible, «Sudoku del día»: cada día hay un sudoku nuevo de 9 por 9, el mismo para todas las personas que usan esta versión del complemento. El nivel depende del día de la semana: lunes y martes, fácil; miércoles y jueves, medio; viernes, difícil; sábado y domingo, fácil.

* Antes de empezar el de cada día se pregunta si quieres jugarlo con ayudas o sin ayudas.
* Tiene su propio guardado: si lo dejas a medias, al volver a abrirlo sigue donde estaba, y no se pierde el sudoku normal que tengas empezado.
* Solo se puede jugar el de hoy. Cuando lo resuelves, se dice cuántos días seguidos llevas. Si un día no lo resuelves, la cuenta vuelve a empezar.
* Si ya lo resolviste, al abrirlo se te recuerda y se te invita a volver mañana.

## Aprender a jugar

Herramientas, MiSudokuAccesible, «Aprender a jugar...». Es un curso guiado de 13 lecciones, pensado también para niñas y niños. Por ahora, las lecciones solo están en español.

1. La lista muestra las lecciones, agrupadas en bloques, con su estado: pendiente, en curso o completada con sus estrellas. Elige una y pulsa Empezar.
2. Se abre la explicación de la lección. Léela con las flechas o deja que NVDA la lea, y pulsa Empezar.
3. Se abre el tablero con el primer ejercicio y se oye la instrucción. Las teclas son las mismas del juego.

Las lecciones:

* **Bloque A, Conocer el sudoku** (en 4 por 4): 1. Las reglas. 2. Filas, columnas y bloques. 3. Escribir, borrar y notas.
* **Bloque B, Las técnicas** (en 6 por 6 y 9 por 9): 4. Último número. 5. Único lugar en un bloque. 6. Único lugar en filas y columnas. 7. Único número. 8. Las notas como ayuda. 9. Intersección. 10. Pareja.
* **Bloque C, A jugar:** sudokus enteros, de principio a fin. 11. Tu primer 4 por 4. 12. Tu primer 6 por 6. 13. Tu primer 9 por 9.

En las lecciones:

* Un número que no va no se escribe: suena el tono de error y se oye por qué, por ejemplo «El 2 ya está en la fila 1. Prueba con otro».
* **F2** repite la instrucción del ejercicio y **Mayúsculas+F2**, la explicación de la lección.
* **P** da una pista breve y **Mayúsculas+P**, una completa.
* Cada ejercicio da **3 estrellas** si lo haces sin pistas, **2** si usaste la pista breve y **1** si usaste la completa. Equivocarse no quita estrellas. En los sudokus enteros del bloque C se cuentan las pistas: 3 estrellas con ninguna o una, 2 con hasta cuatro y 1 con más.
* En los ejercicios de técnicas no se dice la casilla: se dice dónde mirar, porque encontrarla es el ejercicio. Si escribes en otra casilla, se oye «Aquí no» y se repite dónde mirar.
* Los ejercicios de intersección y de pareja tienen dos pasos, y el tablero ya trae las notas puestas en las casillas que importan. En el paso 1 se explica qué se descarta y en qué casilla quitar la nota, por ejemplo «Quita la nota 7 de la fila 3, columna 7»: quítala con Mayúsculas y el número. En el paso 2, con la nota quitada, aparece el número que ya puedes escribir.
* Al terminar un ejercicio, pasa solo al siguiente. Al terminar la lección, el menú del tablero tiene «Siguiente lección», «Practicar esta lección», «Lista de lecciones», «Atajos de teclado» y «Cerrar la lección».
* El progreso se guarda solo. Si cierras una lección a medias, la próxima vez sigue desde el primer ejercicio pendiente. Un sudoku entero del bloque C se guarda tal como estaba, con las pistas que pediste.

### Practicar

Las lecciones del bloque B tienen un botón **Practicar** en la lista de lecciones, y también «Practicar esta lección» en el menú del tablero. Cada ronda tiene 5 ejercicios nuevos de esa técnica, creados en el momento, así que nunca se acaban. El primero puede tardar unos segundos en prepararse; los demás se preparan mientras juegas.

Al terminar la ronda se dicen las estrellas conseguidas, de 15, y tu mejor ronda. Para jugar otra, abre el menú del tablero y elige «Otra ronda de práctica».

## Mis estadísticas

Herramientas, MiSudokuAccesible, «Mis estadísticas...». Se abren en una página que se lee como una web: H salta entre las secciones, y tiene botones para copiar y cerrar.

* **Sudokus resueltos:** cuántos de cada tamaño y nivel, cuántos de ellos sin ayudas, y tu mejor tiempo.
* **Sudoku del día:** días seguidos, récord y total resueltos.
* **Aprender a jugar:** lecciones terminadas, estrellas y la mejor práctica de cada técnica.

## Opciones

En el menú de NVDA, Preferencias, Opciones, categoría MiSudokuAccesible:

* **Decir la posición de las casillas:** larga («Fila 3, columna 5») o corta («F3C5»). Las pistas siempre dicen la posición larga.
* **Al escribir un número, quitar esa nota de su fila, su columna y su bloque** (activado). Las lecciones siempre lo hacen, porque así lo enseñan.
* **Anunciar cuando una fila, columna o bloque está completo** (activado).
* **Reproducir sonidos** (activado). Los tonos de error suenan siempre.
* **Borrar mi progreso y estadísticas:** borra el progreso del curso, la práctica, los días seguidos y las estadísticas. Pide confirmación. Los sudokus a medias se conservan.

## Sobre cómo se hizo este complemento

MiSudokuAccesible nació porque siempre quise jugar al sudoku para ejercitar la concentración y la atención, y porque quería que las personas con discapacidad visual, y en especial niñas y niños, pudieran aprender a jugarlo de forma plena con NVDA. Es el segundo juego de mi colección, después de MiAjedrezAccesible.

Lo desarrollé con la asistencia de Claude, un modelo de inteligencia artificial de Anthropic. Claude escribió la mayor parte del código siguiendo mis indicaciones, consultó la documentación y el código de NVDA y me propuso soluciones técnicas. La dirección y el criterio fueron enteramente míos: el diseño funcional del complemento, el curso y la forma de enseñar, la experiencia sonora, el comportamiento con el lector de pantalla y el descarte de características que no aportaban.

Cada versión, función, atajo y respuesta de voz fue probada y validada por mí directamente con NVDA. Ninguna función llegó a la versión final sin mi revisión y aprobación.

Lo cuento porque creo que es lo honesto. Si encuentras un error, la responsabilidad es mía, y me ayudas mucho si me escribes para corregirlo.

## Autoría

Desarrollado con amor por Wilmer Rodríguez Vega ([wilmer-rv.com](https://wilmer-rv.com)).

Para reportar un error o proponer una mejora, escríbeme a contacto@wilmer-rv.com o abre un reporte en [la página de GitHub del complemento](https://github.com/WilmerRv1989/MiSudokuAccesible/issues).

MiSudokuAccesible se distribuye con la licencia GPL 2 o posterior. Los sudokus se generan en el propio complemento y los sonidos son propios.
