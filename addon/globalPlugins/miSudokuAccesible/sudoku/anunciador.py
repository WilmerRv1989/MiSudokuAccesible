# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Todo lo que se dice del sudoku: casillas, grupos, jugadas y resultados."""

from collections.abc import Iterable

from .generador import Nivel
from .grupos import Grupo, TipoGrupo, forma_de
from .idioma import _, ngettext
from .tablero import Pista, ResultadoEscritura
from .tecnicas import Eliminacion, Paso, Tecnica


def unir(numeros: Iterable[int]) -> str:
	"""«1, 4 y 7»."""
	textos = [str(n) for n in numeros]
	if len(textos) <= 1:
		return "".join(textos)
	# Translators: joins the last two items of a list of numbers, as in "1, 4 and 7".
	return _("{items} and {last}").format(items=", ".join(textos[:-1]), last=textos[-1])


def etiqueta_nivel(nivel: Nivel) -> str:
	return {
		# Translators: a sudoku difficulty level.
		Nivel.FACIL: _("Easy"),
		# Translators: a sudoku difficulty level.
		Nivel.MEDIO: _("Medium"),
		# Translators: a sudoku difficulty level.
		Nivel.DIFICIL: _("Hard"),
	}[nivel]


def etiqueta_tamano(lado: int) -> str:
	# Translators: a size of the sudoku board, as in "9 by 9".
	return _("{size} by {size}").format(size=lado)


def describir_fuera_de_rango(lado: int) -> str:
	# Translators: said when pressing a number that is too big for the board, as in "In this sudoku the numbers go from 1 to 4."
	return _("In this sudoku the numbers go from 1 to {last}.").format(last=lado)


# Casillas.


def describir_notas(notas: Iterable[int]) -> str:
	ordenadas = sorted(notas)
	if not ordenadas:
		# Translators: reported for a cell without notes.
		return _("no notes")
	# Translators: the notes of a cell, as in "notes 1, 4 and 7".
	return _("notes {numbers}").format(numbers=unir(ordenadas))


# Si la posición de las casillas se dice en la forma corta («F3C5»). La cambia el panel de opciones.
_forma_corta = False


def configurar(forma_corta: bool) -> None:
	global _forma_corta
	_forma_corta = forma_corta


def nombre_casilla(fila: int, columna: int) -> str:
	"""«Fila 3, columna 5» o, en la forma corta, «F3C5». Fila y columna desde 1."""
	if _forma_corta:
		# Translators: short form of a cell position, as in "R3C5" (row 3, column 5).
		return _("R{row}C{column}").format(row=fila, column=columna)
	# Translators: a cell position at the start of its description, as in "Row 3, column 5".
	return _("Row {row}, column {column}").format(row=fila, column=columna)


def describir_casilla(
	fila: int,
	columna: int,
	valor: int = 0,
	fija: bool = False,
	notas: Iterable[int] = (),
	bloque: int | None = None,
) -> str:
	"""«Fila 3, columna 5: 7, fija», «Fila 3, columna 5, vacía, notas 1 y 4» y, al cambiar de bloque,
	«bloque 2» al final."""
	casilla = nombre_casilla(fila + 1, columna + 1)
	notas = sorted(notas)
	if fija:
		# Translators: a cell with a number from the puzzle, which cannot be changed, as in "Row 3, column 5: 7, fixed".
		texto = _("{cell}: {number}, fixed").format(cell=casilla, number=valor)
	elif valor:
		# Translators: a cell with a number written by the player, as in "Row 3, column 5: 7".
		texto = _("{cell}: {number}").format(cell=casilla, number=valor)
	elif notas:
		# Translators: an empty cell with notes, as in "Row 3, column 5, empty, notes 1, 4 and 7".
		texto = _("{cell}, empty, {notes}").format(cell=casilla, notes=describir_notas(notas))
	else:
		# Translators: an empty cell, as in "Row 3, column 5, empty".
		texto = _("{cell}, empty").format(cell=casilla)
	if bloque is not None:
		# Translators: a cell of the sudoku board when moving into another 3 by 3 block.
		texto = _("{cell}, block {block}").format(cell=texto, block=bloque)
	return texto


# Filas, columnas y bloques.


def nombre_grupo(grupo: Grupo) -> str:
	if grupo.tipo is TipoGrupo.FILA:
		# Translators: a row of the sudoku board, at the start of a sentence.
		return _("Row {number}").format(number=grupo.numero)
	if grupo.tipo is TipoGrupo.COLUMNA:
		# Translators: a column of the sudoku board, at the start of a sentence.
		return _("Column {number}").format(number=grupo.numero)
	# Translators: a 3 by 3 block of the sudoku board, at the start of a sentence.
	return _("Block {number}").format(number=grupo.numero)


def describir_grupo(grupo: Grupo, numeros: list[int], lado: int = 9) -> str:
	"""«Fila 3: tiene 3, 5 y 7; faltan 1, 2, 4, 6, 8 y 9»."""
	nombre = nombre_grupo(grupo)
	tiene = sorted(numeros)
	faltan = [n for n in range(1, lado + 1) if n not in tiene]
	if not tiene:
		# Translators: reported when reading a row, column or block without numbers, as in "Row 3: no numbers".
		return _("{group}: no numbers").format(group=nombre)
	if not faltan and len(tiene) == lado:
		# Translators: reported when reading a full row, column or block, as in "Row 3: complete".
		return _("{group}: complete").format(group=nombre)
	if not faltan:
		# Translators: reported when reading a full row, column or block with repeated numbers.
		return _("{group}: has {numbers}; numbers are repeated").format(group=nombre, numbers=unir(tiene))
	# Translators: reported when reading a row, column or block, as in "Row 3: has 3, 5 and 7; missing 1, 2, 4, 6, 8 and 9".
	return _("{group}: has {numbers}; missing {missing}").format(
		group=nombre,
		numbers=unir(tiene),
		missing=unir(faltan),
	)


def describir_completado(grupo: Grupo) -> str:
	if grupo.tipo is TipoGrupo.FILA:
		# Translators: said when a row of the sudoku gets its 9 numbers.
		return _("Row {number} complete").format(number=grupo.numero)
	if grupo.tipo is TipoGrupo.COLUMNA:
		# Translators: said when a column of the sudoku gets its 9 numbers.
		return _("Column {number} complete").format(number=grupo.numero)
	# Translators: said when a 3 by 3 block of the sudoku gets its 9 numbers.
	return _("Block {number} complete").format(number=grupo.numero)


# Jugadas.


def _lugar_choque(tipo: TipoGrupo) -> str:
	if tipo is TipoGrupo.FILA:
		# Translators: where a written number clashes, as in "clashes with the 5 in the row".
		return _("in the row")
	if tipo is TipoGrupo.COLUMNA:
		# Translators: where a written number clashes, as in "clashes with the 5 in the column".
		return _("in the column")
	# Translators: where a written number clashes, as in "clashes with the 5 in the block".
	return _("in the block")


def describir_escritura(numero: int, resultado: ResultadoEscritura) -> str:
	"""«7», «7, choca con el 7 de la fila y del bloque» y los grupos completados: «Fila 3 completa»."""
	texto = str(numero)
	if resultado.choques:
		lugares = [_lugar_choque(grupo.tipo) for grupo in resultado.choques]
		if len(lugares) > 1:
			# Translators: joins the places where a number clashes, as in "in the row and in the block".
			lugares_texto = _("{items} and {last}").format(items=", ".join(lugares[:-1]), last=lugares[-1])
		else:
			lugares_texto = lugares[0]
		# Translators: said when a written number is already in its row, column or block.
		texto = _("{number}, clashes with the {number} {places}").format(number=numero, places=lugares_texto)
	partes = [texto, *(describir_completado(grupo) for grupo in resultado.completados)]
	return ". ".join(partes)


def describir_nota(numero: int, puesta: bool) -> str:
	if puesta:
		# Translators: said when a note is added to a cell.
		return _("note {number} added").format(number=numero)
	# Translators: said when a note is removed from a cell.
	return _("note {number} removed").format(number=numero)


def describir_borrado(borrado: int | None) -> str:
	"""Lo que se dice al borrar: el número borrado, las notas, o que la casilla ya estaba vacía."""
	if borrado is None:
		# Translators: said when deleting in a cell that is already empty.
		return _("empty")
	if borrado == 0:
		# Translators: said when deleting the notes of a cell.
		return _("notes deleted")
	# Translators: said when deleting a number, as in "7 deleted".
	return _("{number} deleted").format(number=borrado)


# Estado del sudoku.


def describir_vacias(vacias: int) -> str:
	if vacias == 0:
		# Translators: reported when the sudoku has no empty cells.
		return _("There are no empty cells.")
	# Translators: how many empty cells the sudoku has.
	return ngettext("{count} empty cell left.", "{count} empty cells left.", vacias).format(count=vacias)


def describir_comprobacion(errores: int, vacias: int) -> str:
	"""Cuántas casillas están mal, sin decir cuáles."""
	if errores == 0:
		# Translators: result of checking the sudoku when every written number is right.
		texto = _("Everything you wrote is right.")
	else:
		texto = ngettext(
			# Translators: result of checking the sudoku, without saying which cells are wrong.
			"{count} cell is wrong.",
			"{count} cells are wrong.",
			errores,
		).format(count=errores)
	return f"{texto} {describir_vacias(vacias)}"


def texto_tiempo(segundos: float) -> str:
	total = int(segundos)
	horas, resto = divmod(total, 3600)
	minutos, segundos_ = divmod(resto, 60)
	partes = []
	if horas:
		# Translators: part of a duration.
		partes.append(ngettext("{count} hour", "{count} hours", horas).format(count=horas))
	if minutos:
		# Translators: part of a duration.
		partes.append(ngettext("{count} minute", "{count} minutes", minutos).format(count=minutos))
	if segundos_ or not partes:
		# Translators: part of a duration.
		partes.append(ngettext("{count} second", "{count} seconds", segundos_).format(count=segundos_))
	if len(partes) == 1:
		return partes[0]
	return _("{items} and {last}").format(items=", ".join(partes[:-1]), last=partes[-1])


def describir_resuelto(segundos: float) -> str:
	# Translators: said when the sudoku is solved; the time is only informative.
	return _("Congratulations, you solved the sudoku! Time: {time}.").format(time=texto_tiempo(segundos))


# Pistas.


def posicion(indice: int, lado: int) -> str:
	"""«la fila 3, columna 5», para usar dentro de una frase."""
	fila, columna = divmod(indice, lado)
	# Translators: a cell inside a sentence, as in "the 7 only fits in the row 3, column 5".
	return _("the row {row}, column {column}").format(row=fila + 1, column=columna + 1)


def grupo_en_frase(grupo: Grupo) -> str:
	"""«la fila 3», «la columna 3» o «el bloque 3», para usar dentro de una frase."""
	if grupo.tipo is TipoGrupo.FILA:
		# Translators: a row inside a sentence, as in "Look at the row 3".
		return _("the row {number}").format(number=grupo.numero)
	if grupo.tipo is TipoGrupo.COLUMNA:
		# Translators: a column inside a sentence, as in "Look at the column 3".
		return _("the column {number}").format(number=grupo.numero)
	# Translators: a 3 by 3 block inside a sentence, as in "Look at the block 3".
	return _("the block {number}").format(number=grupo.numero)


def unir_textos(textos: list[str]) -> str:
	"""«la fila 1, columna 2 y la fila 3, columna 4»."""
	if len(textos) <= 1:
		return "".join(textos)
	return _("{items} and {last}").format(items=", ".join(textos[:-1]), last=textos[-1])


def _posiciones(indices: Iterable[int], lado: int) -> str:
	return unir_textos([posicion(i, lado) for i in indices])


def _describir_error(pista: Pista, valor: int, lado: int) -> str:
	assert pista.error is not None
	texto = _(
		# Translators: hint when the board has a wrong number, as in "Before going on, check the row 3, column 5: the 4 is not right."
		"Before going on, check {cell}: the {number} is not right.",
	).format(cell=posicion(pista.error, lado), number=valor)
	if pista.otros_errores:
		otros = ngettext(
			# Translators: added to the hint about a wrong number when there are more.
			"There is {count} more wrong number.",
			"There are {count} more wrong numbers.",
			pista.otros_errores,
		).format(count=pista.otros_errores)
		texto = f"{texto} {otros}"
	return texto


def _describir_revelada(indice: int, numero: int, lado: int) -> str:
	return _(
		# Translators: hint when none of the techniques works; it tells the number of a cell.
		"None of the techniques I know works here, so here is a number: the {number} goes in {cell}.",
	).format(number=numero, cell=posicion(indice, lado))


def describir_pista(pista: Pista | None, valores: list[int], solucion: list[int], completa: bool) -> str:
	"""La pista breve (dónde mirar) o la completa (qué número va, dónde y por qué)."""
	if pista is None:
		# Translators: hint when the sudoku is already solved.
		return _("The sudoku is already solved.")
	lado = forma_de(valores).lado
	if pista.error is not None:
		return _describir_error(pista, valores[pista.error], lado)
	if pista.revelada is not None:
		return _describir_revelada(pista.revelada, solucion[pista.revelada], lado)
	assert pista.paso is not None
	if completa:
		return explicar_paso(pista.paso, lado)
	return orientar_paso(pista.paso, lado)


def orientar_paso(paso: Paso, lado: int) -> str:
	"""La pista breve: dónde mirar y qué buscar, sin decir el número."""
	if paso.eliminaciones:
		# Se nombran por separado dónde va el número y dónde está la razón: suelen ser grupos distintos.
		destino = grupo_en_frase(paso.grupo or Grupo(TipoGrupo.FILA, paso.indice // lado + 1))
		primera = paso.eliminaciones[0]
		if primera.tecnica is Tecnica.INTERSECCION:
			return _(
				# Translators: short hint, as in "You can write a number in the row 3, but first you need an intersection in the block 2."
				"You can write a number in {target}, but first you need an intersection in {group}.",
			).format(target=destino, group=grupo_en_frase(primera.grupo))
		return _(
			# Translators: short hint, as in "You can write a number in the row 2, but first you need a pair in the column 6."
			"You can write a number in {target}, but first you need a pair in {group}.",
		).format(target=destino, group=grupo_en_frase(primera.grupo))
	if paso.tecnica is Tecnica.ULTIMO_NUMERO:
		assert paso.grupo is not None
		# Translators: short hint, as in "Look at the row 3: only one number is missing."
		return _("Look at {group}: only one number is missing.").format(group=grupo_en_frase(paso.grupo))
	if paso.tecnica is Tecnica.UNICO_LUGAR:
		assert paso.grupo is not None
		return _(
			# Translators: short hint, as in "Look at the block 4: there is a number that only fits in one place."
			"Look at {group}: there is a number that only fits in one place.",
		).format(group=grupo_en_frase(paso.grupo))
	fila = paso.indice // lado + 1
	return _(
		# Translators: short hint, as in "Look at the row 2: there is a cell where only one number fits."
		"Look at the row {row}: there is a cell where only one number fits.",
	).format(row=fila)


def explicar_eliminacion(eliminacion: Eliminacion, lado: int) -> str:
	grupo = grupo_en_frase(eliminacion.grupo)
	if eliminacion.tecnica is Tecnica.INTERSECCION:
		assert eliminacion.otro is not None
		return _(
			# Translators: full hint, an intersection, as in "In the block 1, the 5 can only go in the row 1, column 2 and the row 1, column 3, which are also in the row 1. So in the row 1 there cannot be another 5 outside those cells."
			"In {group}, the {number} can only go in {cells}, which are also in {other}. "
			"So in {other} there cannot be another {number} outside those cells.",
		).format(
			group=grupo,
			number=eliminacion.numeros[0],
			cells=_posiciones(eliminacion.casillas, lado),
			other=grupo_en_frase(eliminacion.otro),
		)
	primero, segundo = eliminacion.numeros
	if eliminacion.oculta:
		return _(
			# Translators: full hint, a hidden pair, as in "In the column 6, the 3 and the 8 can only go in the row 2, column 6 and the row 7, column 6. So those two cells cannot have other numbers."
			"In {group}, the {first} and the {second} can only go in {cells}. "
			"So those two cells cannot have other numbers.",
		).format(group=grupo, first=primero, second=segundo, cells=_posiciones(eliminacion.casillas, lado))
	return _(
		# Translators: full hint, a pair, as in "In the column 6, the row 2, column 6 and the row 7, column 6 only accept the 3 and the 8. So in the column 6 no other cell can have a 3 or an 8."
		"In {group}, {cells} only accept the {first} and the {second}. "
		"So in {group} no other cell can have a {first} or a {second}.",
	).format(group=grupo, first=primero, second=segundo, cells=_posiciones(eliminacion.casillas, lado))


def explicar_paso(paso: Paso, lado: int) -> str:
	"""La pista completa: qué número va, dónde y por qué."""
	celda = posicion(paso.indice, lado)
	if paso.tecnica is Tecnica.ULTIMO_NUMERO:
		assert paso.grupo is not None
		# Translators: full hint, as in "In the row 3 only the 6 is missing: it goes in the row 3, column 4."
		return _("In {group} only the {number} is missing: it goes in {cell}.").format(
			group=grupo_en_frase(paso.grupo),
			number=paso.numero,
			cell=celda,
		)
	partes = [explicar_eliminacion(e, lado) for e in paso.eliminaciones]
	if partes:
		# Primero dónde va el número; después, por qué.
		# Translators: start of a full hint with an intersection or a pair, as in "The 8 goes in the row 3, column 7. Why:"
		inicio = _("The {number} goes in {cell}. Why:").format(number=paso.numero, cell=celda)
		partes.insert(0, inicio)
	if paso.tecnica is Tecnica.UNICO_LUGAR:
		assert paso.grupo is not None
		if partes:
			# Translators: full hint after explaining an intersection or a pair, as in "Therefore, in the block 4, the 7 only fits in the row 5, column 2."
			conclusion = _("Therefore, in {group}, the {number} only fits in {cell}.")
		else:
			conclusion = _(
				# Translators: full hint, as in "In the block 4, the 7 only fits in the row 5, column 2: the other empty cells already have a 7 in their row, column or block."
				"In {group}, the {number} only fits in {cell}: "
				"the other empty cells already have a {number} in their row, column or block.",
			)
		partes.append(conclusion.format(group=grupo_en_frase(paso.grupo), number=paso.numero, cell=celda))
	elif partes:
		# Translators: full hint after explaining an intersection or a pair, as in "Therefore, only the 4 fits in the row 2, column 8."
		conclusion = _("Therefore, only the {number} fits in {cell}.")
		partes.append(conclusion.format(number=paso.numero, cell=celda))
	else:
		conclusion = _(
			# Translators: full hint, as in "Only the 4 fits in the row 2, column 8: the other numbers are already in its row, column or block."
			"Only the {number} fits in {cell}: the other numbers are already in its row, column or block.",
		)
		partes.append(conclusion.format(number=paso.numero, cell=celda))
	return " ".join(partes)
