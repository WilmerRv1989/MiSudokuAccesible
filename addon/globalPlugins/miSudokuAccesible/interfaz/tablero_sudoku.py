# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""El tablero de sudoku como cuadrícula virtual: casillas y teclas."""

from dataclasses import replace
from typing import TYPE_CHECKING

import addonHandler
import core
import tones
import ui
import wx
from scriptHandler import script

from ..nucleo.tablero_virtual import CeldaVirtual, CuadriculaVirtual
from ..sudoku import anunciador
from ..sudoku.grupos import TipoGrupo
from . import preferencias, sonidos

if TYPE_CHECKING:
	from ..sudoku.tablero import Sudoku
	from .ventana_tablero import VentanaSudoku

addonHandler.initTranslation()

# Translators: category of the add-on commands in the Input gestures dialog.
CATEGORIA = _("MiSudokuAccesible")

# Tonos: no se puede (casilla fija, nada que deshacer) y número que choca.
TONO_ERROR = (220, 80)
_TONO_CHOQUE = (330, 120)

# Las teclas de los números, del 1 al 9: en los tableros pequeños, las más altas avisan del error.
_NUMEROS = [str(n) for n in range(1, 10)]

# Si tras un menú o un diálogo el foco no vuelve a la casilla, el mensaje pendiente se dice igual.
_ESPERA_FOCO_MS = 1500


class CeldaSudoku(CeldaVirtual):
	"""Casilla del tablero. Aquí están todas las teclas que funcionan dentro del tablero."""

	cuadricula: "CuadriculaSudoku"

	# Navegación.

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Moves to the cell above"),
		category=CATEGORIA,
		gesture="kb:upArrow",
	)
	def script_arriba(self, gesture) -> None:
		self.cuadricula.mover(-1, 0)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Moves to the cell below"),
		category=CATEGORIA,
		gesture="kb:downArrow",
	)
	def script_abajo(self, gesture) -> None:
		self.cuadricula.mover(1, 0)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Moves to the cell on the left"),
		category=CATEGORIA,
		gesture="kb:leftArrow",
	)
	def script_izquierda(self, gesture) -> None:
		self.cuadricula.mover(0, -1)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Moves to the cell on the right"),
		category=CATEGORIA,
		gesture="kb:rightArrow",
	)
	def script_derecha(self, gesture) -> None:
		self.cuadricula.mover(0, 1)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Moves to the first cell of the row"),
		category=CATEGORIA,
		gesture="kb:home",
	)
	def script_inicio_fila(self, gesture) -> None:
		self.cuadricula.ir_a(self.cuadricula.fila, 0)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Moves to the last cell of the row"),
		category=CATEGORIA,
		gesture="kb:end",
	)
	def script_fin_fila(self, gesture) -> None:
		self.cuadricula.ir_a(self.cuadricula.fila, self.cuadricula.columnas - 1)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Moves to the next empty cell"),
		category=CATEGORIA,
		gesture="kb:tab",
	)
	def script_siguiente_vacia(self, gesture) -> None:
		self.cuadricula.ir_a_vacia(1)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Moves to the previous empty cell"),
		category=CATEGORIA,
		gesture="kb:shift+tab",
	)
	def script_anterior_vacia(self, gesture) -> None:
		self.cuadricula.ir_a_vacia(-1)

	# Escribir.

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Writes that number in the cell"),
		category=CATEGORIA,
		gestures=[f"kb:{n}" for n in _NUMEROS],
	)
	def script_escribir(self, gesture) -> None:
		self.cuadricula.escribir(int(gesture.mainKeyName))

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Adds or removes that number as a note of the cell"),
		category=CATEGORIA,
		gestures=[f"kb:shift+{n}" for n in _NUMEROS],
	)
	def script_nota(self, gesture) -> None:
		self.cuadricula.alternar_nota(int(gesture.mainKeyName))

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Deletes the number of the cell or, if it has none, its notes"),
		category=CATEGORIA,
		gestures=["kb:delete", "kb:backspace"],
	)
	def script_borrar(self, gesture) -> None:
		self.cuadricula.borrar()

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Undoes the last change"),
		category=CATEGORIA,
		gesture="kb:control+z",
	)
	def script_deshacer(self, gesture) -> None:
		self.cuadricula.deshacer()

	# Pistas.

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Gives a short hint: where to look and what to look for"),
		category=CATEGORIA,
		gesture="kb:p",
	)
	def script_pista(self, gesture) -> None:
		self.cuadricula.dar_pista(completa=False)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Gives a full hint: which number goes where, and why"),
		category=CATEGORIA,
		gesture="kb:shift+p",
	)
	def script_pista_completa(self, gesture) -> None:
		self.cuadricula.dar_pista(completa=True)

	# Información.

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Reports the notes of the cell"),
		category=CATEGORIA,
		gesture="kb:n",
	)
	def script_leer_notas(self, gesture) -> None:
		ui.message(anunciador.describir_notas(self.cuadricula.sudoku.notas[self.cuadricula.indice]))

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Reports which numbers the row has and which are missing"),
		category=CATEGORIA,
		gesture="kb:f",
	)
	def script_leer_fila(self, gesture) -> None:
		self.cuadricula.leer_grupo(TipoGrupo.FILA)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Reports which numbers the column has and which are missing"),
		category=CATEGORIA,
		gesture="kb:c",
	)
	def script_leer_columna(self, gesture) -> None:
		self.cuadricula.leer_grupo(TipoGrupo.COLUMNA)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Reports which numbers the block has and which are missing"),
		category=CATEGORIA,
		gesture="kb:b",
	)
	def script_leer_bloque(self, gesture) -> None:
		self.cuadricula.leer_grupo(TipoGrupo.BLOQUE)

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Reports how many empty cells are left"),
		category=CATEGORIA,
		gesture="kb:f5",
	)
	def script_vacias(self, gesture) -> None:
		ui.message(anunciador.describir_vacias(self.cuadricula.sudoku.vacias()))

	# Ventana.

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Opens the menu of the board"),
		category=CATEGORIA,
		gestures=["kb:applications", "kb:shift+f10"],
	)
	def script_menu(self, gesture) -> None:
		self.cuadricula.ventana.mostrar_menu_tablero()

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Shows the keyboard shortcuts of this window"),
		category=CATEGORIA,
	)
	def script_atajos(self, gesture) -> None:
		self.cuadricula.ventana.mostrar_atajos()

	@script(
		# Translators: description of a sudoku board command in the Input gestures dialog.
		description=_("Closes the board; the sudoku is kept to continue it later"),
		category=CATEGORIA,
		gesture="kb:escape",
	)
	def script_cerrar(self, gesture) -> None:
		wx.CallAfter(self.cuadricula.ventana.Close)


class CuadriculaSudoku(CuadriculaVirtual):
	"""Tablero de 9, 6 o 4 casillas de lado. El número de bloque se dice al entrar en el tablero
	y al cambiar de bloque."""

	clase_celda = CeldaSudoku

	def __init__(self, panel: wx.Window, ventana: "VentanaSudoku") -> None:
		lado = ventana.sudoku.forma.lado
		super().__init__(panel, lado, lado)
		self.ventana = ventana
		# Bloque que se dijo por última vez; None hace que se vuelva a decir.
		self._bloque_anunciado: int | None = None
		# Mensaje que se dirá cuando NVDA termine de anunciar la casilla (ver `decir_al_volver`).
		self._pendiente: str | None = None

	@property
	def sudoku(self) -> "Sudoku":
		return self.ventana.sudoku

	@property
	def indice(self) -> int:
		return self.fila * self.columnas + self.columna

	def olvidar_bloque(self) -> None:
		"""La próxima casilla que se anuncie dirá su bloque (por ejemplo, al volver a la ventana)."""
		self._bloque_anunciado = None

	def describir(self, fila: int, columna: int, con_bloque: bool = False) -> str:
		indice = fila * self.columnas + columna
		sudoku = self.sudoku
		return anunciador.describir_casilla(
			fila,
			columna,
			sudoku.valores[indice],
			sudoku.es_fija(indice),
			sudoku.notas[indice],
			sudoku.forma.bloque(fila, columna) if con_bloque else None,
		)

	def nombre_celda(self, fila: int, columna: int) -> str:
		return self.describir(
			fila,
			columna,
			self.sudoku.forma.bloque(fila, columna) != self._bloque_anunciado,
		)

	def al_enfocar_celda(self, fila: int, columna: int) -> None:
		self._bloque_anunciado = self.sudoku.forma.bloque(fila, columna)
		super().al_enfocar_celda(fila, columna)
		self._decir_pendiente()

	def decir_al_volver(self, texto: str) -> None:
		"""Dice un texto después de que NVDA anuncie la ventana y la casilla al cerrar un menú o un diálogo.

		`ui.delayedMessage` no basta: espera solo un instante, y el anuncio de la casilla lo corta.
		"""
		self._pendiente = texto
		core.callLater(_ESPERA_FOCO_MS, self._decir_pendiente)

	def _decir_pendiente(self) -> None:
		if self._pendiente is None:
			return
		texto, self._pendiente = self._pendiente, None
		ui.message(texto)

	# Moverse.

	def ir_a_vacia(self, paso: int) -> None:
		destino = self.sudoku.siguiente_vacia(self.indice, paso)
		if destino is None:
			ui.message(anunciador.describir_vacias(0))
			return
		self.ir_a(*divmod(destino, self.columnas))

	# Cambios.

	def _avisar_si_resuelto(self) -> bool:
		"""Un sudoku resuelto ya no se cambia: suena el tono de error."""
		if not self.sudoku.resuelto:
			return False
		tones.beep(*TONO_ERROR)
		# Translators: reported when trying to change a solved sudoku.
		ui.message(_("The sudoku is solved. To play another one, open the menu and choose New sudoku."))
		return True

	def _se_puede_cambiar(self) -> bool:
		"""En una casilla fija o en un sudoku resuelto no se cambia nada: suena el tono de error."""
		if self._avisar_si_resuelto():
			return False
		if self.sudoku.es_fija(self.indice):
			tones.beep(*TONO_ERROR)
			# Translators: reported when trying to change a cell with a number from the puzzle.
			ui.message(_("fixed"))
			return False
		return True

	def _numero_valido(self, numero: int) -> bool:
		if numero <= self.sudoku.forma.lado:
			return True
		tones.beep(*TONO_ERROR)
		ui.message(anunciador.describir_fuera_de_rango(self.sudoku.forma.lado))
		return False

	def _tras_cambio(self) -> None:
		self.panel.Refresh()
		self.ventana.al_cambiar()

	def escribir(self, numero: int) -> None:
		if not self._numero_valido(numero) or not self._se_puede_cambiar():
			return
		if self.sudoku.valores[self.indice] == numero:
			ui.message(str(numero))
			return
		resultado = self.sudoku.escribir(self.indice, numero, preferencias.notas_automaticas())
		self._tras_cambio()
		if resultado.resuelto:
			self.ventana.al_resolver()
			return
		if not self.sudoku.ayudas:
			# Sin ayudas, un número que choca se escribe sin avisar, como en papel.
			resultado = replace(resultado, choques=[])
		if not preferencias.anunciar_completados():
			resultado = replace(resultado, completados=[])
		if resultado.choques:
			tones.beep(*_TONO_CHOQUE)
		elif resultado.completados:
			sonidos.reproducir(sonidos.COMPLETADO)
		ui.message(anunciador.describir_escritura(numero, resultado))

	def alternar_nota(self, numero: int) -> None:
		if not self._numero_valido(numero) or not self._se_puede_cambiar():
			return
		if self.sudoku.valores[self.indice]:
			tones.beep(*TONO_ERROR)
			# Translators: reported when adding a note to a cell that already has a number.
			ui.message(_("The cell has a number. Delete it to write notes."))
			return
		puesta = self.sudoku.alternar_nota(self.indice, numero)
		self._tras_cambio()
		ui.message(anunciador.describir_nota(numero, puesta))

	def borrar(self) -> None:
		if not self._se_puede_cambiar():
			return
		borrado = self.sudoku.borrar(self.indice)
		if borrado is not None:
			self._tras_cambio()
		ui.message(anunciador.describir_borrado(borrado))

	def deshacer(self) -> None:
		if self._avisar_si_resuelto():
			return
		indice = self.sudoku.deshacer()
		if indice is None:
			tones.beep(*TONO_ERROR)
			# Translators: reported when there is nothing to undo.
			ui.message(_("There is nothing to undo."))
			return
		self._tras_cambio()
		# Translators: said after undoing, followed by the cell that changed, as in "Undone: row 3, column 5, empty".
		ui.message(_("Undone: {cell}").format(cell=self.describir(*divmod(indice, self.columnas))))

	# Información.

	def dar_pista(self, completa: bool) -> None:
		"""La pista no escribe nada: dice dónde mirar o qué número va, y por qué."""
		sudoku = self.sudoku
		if not sudoku.ayudas:
			tones.beep(*TONO_ERROR)
			# Translators: said when asking for a hint in a sudoku without help.
			ui.message(_("This sudoku is without help."))
			return
		ui.message(anunciador.describir_pista(sudoku.pista(), sudoku.valores, sudoku.solucion, completa))

	def leer_grupo(self, tipo: TipoGrupo) -> None:
		grupo = self.sudoku.forma.grupo_de(self.indice, tipo)
		ui.message(anunciador.describir_grupo(grupo, self.sudoku.numeros_de(grupo), self.columnas))
