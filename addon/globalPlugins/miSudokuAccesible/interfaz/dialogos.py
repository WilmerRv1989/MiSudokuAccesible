# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Diálogos del complemento."""

import addonHandler
import wx
from gui import guiHelper

from ..sudoku import anunciador
from ..sudoku.generador import Nivel, niveles_de
from ..sudoku.grupos import FORMAS, Forma

addonHandler.initTranslation()


class DialogoNuevoSudoku(wx.Dialog):
	"""Elegir el tamaño, el nivel y las ayudas de un sudoku nuevo. Empieza con lo elegido la vez anterior."""

	def __init__(self, padre: wx.Window | None, forma: Forma, nivel: Nivel, ayudas: bool) -> None:
		# Translators: title of the new sudoku dialog.
		super().__init__(padre, title=_("New sudoku"))
		self._formas = sorted(FORMAS.values(), key=lambda f: f.lado)
		self._niveles: list[Nivel] = []
		principal = wx.BoxSizer(wx.VERTICAL)
		ayudante = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.tamano: wx.Choice = ayudante.addLabeledControl(
			# Translators: label of the board size choice in the new sudoku dialog.
			_("&Size:"),
			wx.Choice,
			choices=[anunciador.etiqueta_tamano(f.lado) for f in self._formas],
		)
		self.nivel: wx.Choice = ayudante.addLabeledControl(
			# Translators: label of the difficulty level choice in the new sudoku dialog.
			_("&Level:"),
			wx.Choice,
		)
		self.ayudas: wx.Choice = ayudante.addLabeledControl(
			# Translators: label of the choice of hints and clash warnings in the new sudoku dialog.
			_("&Help:"),
			wx.Choice,
			choices=[
				# Translators: an option of the Help choice in the new sudoku dialog.
				_("On: hints and clash warnings"),
				# Translators: an option of the Help choice in the new sudoku dialog.
				_("Off: no hints or clash warnings"),
			],
		)
		self.ayudas.SetSelection(0 if ayudas else 1)
		ayudante.addDialogDismissButtons(wx.OK | wx.CANCEL, separated=True)
		principal.Add(ayudante.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.SetSizer(principal)
		self.tamano.SetSelection(self._formas.index(forma))
		self._actualizar_niveles(nivel)
		self.tamano.Bind(wx.EVT_CHOICE, lambda evento: self._actualizar_niveles(self.nivel_elegido()))
		principal.Fit(self)
		self.CentreOnScreen()
		self.tamano.SetFocus()

	def _actualizar_niveles(self, preferido: Nivel) -> None:
		"""Los tableros pequeños no tienen nivel difícil: se queda el más cercano al preferido."""
		self._niveles = niveles_de(self.forma_elegida())
		self.nivel.SetItems([anunciador.etiqueta_nivel(n) for n in self._niveles])
		if preferido not in self._niveles:
			preferido = self._niveles[-1]
		self.nivel.SetSelection(self._niveles.index(preferido))

	def ayudas_elegidas(self) -> bool:
		return self.ayudas.GetSelection() == 0

	def forma_elegida(self) -> Forma:
		return self._formas[self.tamano.GetSelection()]

	def nivel_elegido(self) -> Nivel:
		if not self._niveles:
			return Nivel.FACIL
		return self._niveles[self.nivel.GetSelection()]
