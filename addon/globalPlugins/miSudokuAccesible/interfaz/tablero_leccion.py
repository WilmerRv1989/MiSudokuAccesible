# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""El tablero de las lecciones: las mismas teclas que el juego, pero cada cambio lo decide el ejercicio."""

from typing import TYPE_CHECKING

import addonHandler
import tones
import ui
from scriptHandler import script

from ..sudoku.curso.sesion import Respuesta
from . import sonidos
from .tablero_sudoku import CATEGORIA, TONO_ERROR, CeldaSudoku, CuadriculaSudoku

if TYPE_CHECKING:
	from .ventana_leccion import VentanaLeccion

addonHandler.initTranslation()


class CeldaLeccion(CeldaSudoku):
	cuadricula: "CuadriculaLeccion"

	@script(
		# Translators: description of a lesson command in the Input gestures dialog.
		description=_("Repeats the instruction of the exercise"),
		category=CATEGORIA,
		gesture="kb:f2",
	)
	def script_repetir_instruccion(self, gesture) -> None:
		self.cuadricula.ventana.repetir_instruccion()

	@script(
		# Translators: description of a lesson command in the Input gestures dialog.
		description=_("Repeats the explanation of the lesson"),
		category=CATEGORIA,
		gesture="kb:shift+f2",
	)
	def script_repetir_explicacion(self, gesture) -> None:
		self.cuadricula.ventana.repetir_explicacion()


class CuadriculaLeccion(CuadriculaSudoku):
	clase_celda = CeldaLeccion
	ventana: "VentanaLeccion"

	def escribir(self, numero: int) -> None:
		if self._numero_valido(numero):
			self._responder(self.ventana.sesion.escribir(self.indice, numero))

	def alternar_nota(self, numero: int) -> None:
		if self._numero_valido(numero):
			self._responder(self.ventana.sesion.alternar_nota(self.indice, numero))

	def borrar(self) -> None:
		self._responder(self.ventana.sesion.borrar(self.indice))

	def deshacer(self) -> None:
		tones.beep(*TONO_ERROR)
		# Translators: said when pressing Control+Z in a lesson.
		ui.message(_("In the lessons there is nothing to undo: a number that does not fit is not written."))

	def dar_pista(self, completa: bool) -> None:
		ui.message(self.ventana.sesion.pista(completa))
		# Las pistas pedidas cuentan para las estrellas: se guardan aunque se cierre la ventana.
		self.ventana.al_cambiar()

	def _responder(self, respuesta: Respuesta) -> None:
		if respuesta.error:
			tones.beep(*TONO_ERROR)
		if respuesta.aceptada:
			self.panel.Refresh()
			self.ventana.al_cambiar()
		if respuesta.superado:
			self.ventana.al_superar(respuesta.mensaje)
			return
		if respuesta.nuevo_paso:
			sonidos.reproducir(sonidos.EXITO)
		elif respuesta.completados:
			sonidos.reproducir(sonidos.COMPLETADO)
		ui.message(respuesta.mensaje)
