# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""«Atajos de teclado»: las teclas de cada ventana, tal como las tiene asignadas cada persona.

Las teclas se consultan a NVDA en el momento (como el diálogo Gestos de entrada), así que la
lista refleja los cambios hechos en Gestos de entrada.
"""

from collections.abc import Iterable
from enum import StrEnum
from html import escape

import addonHandler
import inputCore
import ui
from logHandler import log

addonHandler.initTranslation()

# Paquete del complemento, para reconocer las órdenes globales (las del menú Herramientas).
_PAQUETE = __name__.rsplit(".interfaz", 1)[0]


class Contexto(StrEnum):
	JUEGO = "juego"
	LECCION = "leccion"


# Una entrada: las órdenes que agrupa (o None si la tecla es fija, como Alt+F4), las teclas fijas
# en ese caso, y la descripción.
Entrada = tuple[tuple[str, ...] | None, str, str]


def _moverse() -> tuple[str, list[Entrada]]:
	return (
		# Translators: heading in the list of keyboard shortcuts.
		_("Moving around the board"),
		[
			# Translators: description in the list of keyboard shortcuts.
			(("arriba", "abajo", "izquierda", "derecha"), "", _("Move between the cells")),
			# Translators: description in the list of keyboard shortcuts.
			(("inicio_fila", "fin_fila"), "", _("First or last cell of the row")),
			# Translators: description in the list of keyboard shortcuts.
			(("siguiente_vacia", "anterior_vacia"), "", _("Next or previous empty cell")),
		],
	)


def _escribir(contexto: Contexto) -> tuple[str, list[Entrada]]:
	entradas: list[Entrada] = [
		# Translators: description in the list of keyboard shortcuts.
		(("escribir",), "", _("Write that number")),
		# Translators: description in the list of keyboard shortcuts.
		(("nota",), "", _("Add or remove that number as a note")),
		# Translators: description in the list of keyboard shortcuts.
		(("borrar",), "", _("Delete the number of the cell or, if it has none, its notes")),
	]
	if contexto is Contexto.JUEGO:
		# Translators: description in the list of keyboard shortcuts.
		entradas.append((("deshacer",), "", _("Undo the last change")))
	else:
		# Translators: description in the list of keyboard shortcuts, in lessons.
		entradas.append((None, "", _("In the lessons, a number that does not fit is not written")))
	# Translators: heading in the list of keyboard shortcuts.
	return _("Writing"), entradas


def _informacion() -> tuple[str, list[Entrada]]:
	return (
		# Translators: heading in the list of keyboard shortcuts.
		_("Information"),
		[
			# Translators: description in the list of keyboard shortcuts.
			(("leer_notas",), "", _("Notes of the cell")),
			# Translators: description in the list of keyboard shortcuts.
			(("leer_fila",), "", _("Which numbers the row has and which are missing")),
			# Translators: description in the list of keyboard shortcuts.
			(("leer_columna",), "", _("Which numbers the column has and which are missing")),
			# Translators: description in the list of keyboard shortcuts.
			(("leer_bloque",), "", _("Which numbers the block has and which are missing")),
			# Translators: description in the list of keyboard shortcuts.
			(("vacias",), "", _("How many empty cells are left")),
		],
	)


def _pistas(contexto: Contexto) -> tuple[str, list[Entrada]]:
	entradas: list[Entrada] = [
		# Translators: description in the list of keyboard shortcuts.
		(("pista",), "", _("Short hint: where to look and what to look for")),
		# Translators: description in the list of keyboard shortcuts.
		(("pista_completa",), "", _("Full hint: which number goes where, and why")),
	]
	if contexto is Contexto.JUEGO:
		# Translators: description in the list of keyboard shortcuts.
		entradas.append((None, "", _("In a sudoku without help there are no hints")))
	# Translators: heading in the list of keyboard shortcuts.
	return _("Hints"), entradas


def _lecciones() -> tuple[str, list[Entrada]]:
	return (
		# Translators: heading in the list of keyboard shortcuts.
		_("Lessons"),
		[
			# Translators: description in the list of keyboard shortcuts.
			(("repetir_instruccion",), "", _("Repeat the instruction of the exercise")),
			# Translators: description in the list of keyboard shortcuts.
			(("repetir_explicacion",), "", _("Repeat the explanation of the lesson")),
		],
	)


def _ventana(contexto: Contexto) -> tuple[str, list[Entrada]]:
	menus = {
		# Translators: description in the list of keyboard shortcuts.
		Contexto.JUEGO: _("Board menu: new sudoku, check, restart, keyboard shortcuts and close"),
		Contexto.LECCION: _(
			# Translators: description in the list of keyboard shortcuts.
			"Lesson menu: next lesson, practice, list of lessons, keyboard shortcuts and close",
		),
	}
	return (
		# Translators: heading in the list of keyboard shortcuts.
		_("Menu and window"),
		[
			(("menu",), "", menus[contexto]),
			# Translators: description in the list of keyboard shortcuts.
			(("atajos",), "", _("This list of keyboard shortcuts")),
			# Translators: description in the list of keyboard shortcuts.
			(("cerrar",), "", _("Close the window; the sudoku and the progress are kept")),
			# Translators: description in the list of keyboard shortcuts.
			(None, "Alt+F4", _("Close the window")),
		],
	)


def _globales() -> tuple[str, list[Entrada]]:
	return (
		# Translators: heading in the list of keyboard shortcuts: commands that work from anywhere.
		_("From anywhere"),
		[
			# Translators: description in the list of keyboard shortcuts.
			(("abrir_tablero",), "", _("Open the board: continue the unfinished sudoku or start a new one")),
			# Translators: description in the list of keyboard shortcuts.
			(("sudoku_del_dia",), "", _("Open the sudoku of the day")),
			# Translators: description in the list of keyboard shortcuts.
			(("aprender_a_jugar",), "", _("Open Learn to play")),
			# Translators: description in the list of keyboard shortcuts.
			(("estadisticas",), "", _("Show My statistics")),
		],
	)


def secciones(contexto: Contexto) -> list[tuple[str, list[Entrada]]]:
	lista = [_moverse(), _escribir(contexto), _informacion(), _pistas(contexto)]
	if contexto is Contexto.LECCION:
		lista.append(_lecciones())
	lista.append(_ventana(contexto))
	return lista


def teclas_asignadas(objeto: object) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
	"""Teclas de cada orden: (las del tablero de `objeto`, las globales del complemento).

	Se consultan a NVDA como en Gestos de entrada, incluidos los cambios de cada persona.
	"""
	tablero: dict[str, list[str]] = {}
	globales: dict[str, list[str]] = {}
	try:
		mapeos = inputCore.manager.getAllGestureMappings(obj=objeto, ancestors=[])
	except Exception:
		log.debugWarning("No se pudieron consultar los gestos", exc_info=True)
		return tablero, globales
	for categoria in mapeos.values():
		for info in categoria.values():
			nombre = info.scriptName
			if isinstance(objeto, info.cls):
				tablero.setdefault(nombre, []).extend(info.gestures)
			elif info.cls.__module__ == _PAQUETE:
				globales.setdefault(nombre, []).extend(info.gestures)
	return tablero, globales


def _texto_teclas(gestos: Iterable[str]) -> str:
	textos = []
	for gesto in gestos:
		try:
			texto = inputCore.getDisplayTextForGestureIdentifier(gesto)[1]
		except Exception:
			texto = gesto.split(":", 1)[-1]
		if texto not in textos:
			textos.append(texto)
	# Translators: shown in the list of keyboard shortcuts when a command has no key.
	return ", ".join(textos) if textos else _("no key assigned")


def _html_seccion(titulo: str, entradas: list[Entrada], teclas: dict[str, list[str]]) -> str:
	elementos = []
	for ordenes, fija, descripcion in entradas:
		if ordenes is None:
			linea = f"{fija}: {descripcion}" if fija else descripcion
		else:
			gestos = [g for orden in ordenes for g in teclas.get(orden, [])]
			linea = f"{_texto_teclas(gestos)}: {descripcion}"
		elementos.append(f"<li>{escape(linea)}.</li>")
	return f"<h2>{escape(titulo)}</h2><ul>{''.join(elementos)}</ul>"


def html_atajos(contextos: dict[Contexto, object]) -> str:
	"""La lista para uno o varios contextos. `contextos` asocia cada contexto con una casilla de su tablero."""
	intro = _(
		# Translators: introduction of the list of keyboard shortcuts.
		"You can change these keys in the NVDA menu, Preferences, Input gestures, "
		"category MiSudokuAccesible (with the focus on the board for the board keys).",
	)
	partes = [f"<p>{escape(intro)}</p>"]
	vistas: set[str] = set()
	globales: dict[str, list[str]] = {}
	for contexto, objeto in contextos.items():
		teclas, globales = teclas_asignadas(objeto)
		for titulo, entradas in secciones(contexto):
			if len(contextos) > 1:
				# Varias ventanas: las secciones comunes solo una vez.
				if titulo in vistas:
					continue
				vistas.add(titulo)
			partes.append(_html_seccion(titulo, entradas, teclas))
	titulo, entradas = _globales()
	partes.append(_html_seccion(titulo, entradas, globales))
	return "".join(partes)


def mostrar(contextos: dict[Contexto, object]) -> None:
	ui.browseableMessage(
		html_atajos(contextos),
		# Translators: title of the window with the list of keyboard shortcuts.
		title=_("Keyboard shortcuts"),
		isHtml=True,
		closeButton=True,
		copyButton=True,
	)
