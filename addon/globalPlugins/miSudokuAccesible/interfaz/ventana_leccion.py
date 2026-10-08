# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Ventana de una lección: el tablero del ejercicio, la instrucción y el menú de la lección."""

from typing import TYPE_CHECKING

import addonHandler
import ui
import wx

from ..sudoku.curso.modelo import Leccion
from ..sudoku.curso.sesion import SesionEjercicio
from ..sudoku.tablero import Sudoku
from . import atajos
from .tablero_leccion import CuadriculaLeccion
from .ventana_tablero import VentanaBase

if TYPE_CHECKING:
	from .curso import ControladorCurso

addonHandler.initTranslation()


def titulo_leccion(leccion: Leccion) -> str:
	# Translators: title of a lesson, as in "Lesson 1: The rules".
	return _("Lesson {id}: {title}").format(id=leccion.id, title=leccion.titulo)


def titulo_practica(leccion: Leccion) -> str:
	# Translators: title of a practice round, as in "Practice: Lesson 4: Last number".
	return _("Practice: {lesson}").format(lesson=titulo_leccion(leccion))


class VentanaLeccion(VentanaBase):
	"""Ventana de una lección o de una ronda de práctica.

	Se cierra con Escape, con Alt+F4 o desde su menú. El progreso ya está guardado.
	"""

	cuadricula: CuadriculaLeccion

	def __init__(
		self,
		controlador: "ControladorCurso",
		leccion: Leccion,
		sesion: SesionEjercicio,
		numero: int,
		total: int,
		practica: bool = False,
	) -> None:
		super().__init__(
			titulo_practica(leccion) if practica else titulo_leccion(leccion),
			# Translators: accessible name of the sudoku board.
			_("Sudoku board"),
			controlador.al_cerrar_ventana,
		)
		self.controlador = controlador
		self.leccion = leccion
		self.sesion = sesion
		self.numero = numero
		self.total = total
		self.practica = practica
		self._instalar(CuadriculaLeccion(self.panel, self))
		self._poner_cursor()

	@property
	def sudoku(self) -> Sudoku:
		return self.sesion.sudoku

	def _poner_cursor(self) -> None:
		"""El cursor empieza donde dice el ejercicio, sin anunciarlo: lo dice la instrucción."""
		self.cuadricula.fila, self.cuadricula.columna = divmod(
			self.sesion.ejercicio.inicio,
			self.cuadricula.columnas,
		)
		self.cuadricula.olvidar_bloque()
		self.panel.Refresh()

	def _al_mostrar_por_primera_vez(self) -> None:
		texto = self.texto_instruccion()
		if self.sesion.continuada:
			# Translators: said when a whole sudoku of a lesson continues where it was left.
			continuada = _("You continue where you left it.")
			texto = f"{texto} {continuada}"
		self.cuadricula.decir_al_volver(texto)

	def al_cambiar(self) -> None:
		"""Tras cada cambio o pista: un sudoku entero de una lección se guarda para continuarlo."""
		self.controlador.guardar_en_curso()

	def _al_activar(self, evento: wx.ActivateEvent) -> None:
		if evento.GetActive():
			# Al volver a la ventana se dice también el bloque de la casilla.
			self.cuadricula.olvidar_bloque()
		super()._al_activar(evento)

	def cargar(self, sesion: SesionEjercicio, numero: int) -> None:
		"""Pasa al ejercicio siguiente en la misma ventana. Si cambia el tamaño, cambia la cuadrícula."""
		forma_anterior = self.sudoku.forma
		self.sesion = sesion
		self.numero = numero
		if sesion.sudoku.forma is not forma_anterior:
			self.cuadricula.cerrar()
			self._instalar(CuadriculaLeccion(self.panel, self))
			self._poner_cursor()
			# NVDA tenía el foco en una casilla de la cuadrícula anterior: pasa a la nueva.
			self.cuadricula.enfocar_celda_actual()
			return
		self._poner_cursor()

	def texto_instruccion(self) -> str:
		# Translators: before the instruction of an exercise, as in "Exercise 2 of 4."
		ejercicio = _("Exercise {number} of {total}.").format(number=self.numero + 1, total=self.total)
		return f"{ejercicio} {self.sesion.ejercicio.instruccion}"

	def repetir_instruccion(self) -> None:
		ui.message(self.texto_instruccion())

	def repetir_explicacion(self) -> None:
		ui.message(" ".join(self.leccion.explicacion))

	def al_superar(self, mensaje: str) -> None:
		self.controlador.al_superar(mensaje)

	def mostrar_menu_tablero(self) -> None:
		controlador = self.controlador
		hay_siguiente = controlador.curso.siguiente(self.leccion) is not None
		tiene_practica = self.leccion.practica is not None
		if self.practica:
			# Translators: item of the menu of a practice round.
			primeras = [(_("&Another practice round"), self._practicar, True)]
		else:
			primeras = [
				# Translators: item of the menu of a lesson.
				(_("&Next lesson"), controlador.siguiente_leccion, hay_siguiente),
				# Translators: item of the menu of a lesson.
				(_("&Practice this lesson"), self._practicar, tiene_practica),
			]
		self.mostrar_menu(
			[
				*primeras,
				# Translators: item of the menu of a lesson.
				(_("&List of lessons..."), controlador.abrir_lista, True),
				(_("&Keyboard shortcuts"), self.mostrar_atajos, True),
				# Translators: item of the menu of a lesson.
				(_("&Close the lesson"), self.Close, True),
			],
		)

	def mostrar_atajos(self) -> None:
		wx.CallAfter(atajos.mostrar, {atajos.Contexto.LECCION: self.cuadricula.celda_actual})

	def _practicar(self) -> None:
		self.controlador.practicar(self.leccion)
