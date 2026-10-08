# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Panel del complemento en las opciones de NVDA (Preferencias, Opciones, MiSudokuAccesible)."""

from collections.abc import Callable
from typing import ClassVar

import addonHandler
import ui
import wx
from gui import guiHelper
from gui.message import MessageDialog, ReturnCode
from gui.settingsDialogs import SettingsPanel

from . import preferencias

addonHandler.initTranslation()


class PanelMiSudoku(SettingsPanel):
	# Translators: title of the add-on panel in NVDA's settings.
	title = _("MiSudokuAccesible")
	# Lo pone el complemento: borra el progreso y las estadísticas, y devuelve True si se pudo.
	al_borrar_progreso: ClassVar[Callable[[], bool] | None] = None

	def makeSettings(self, settingsSizer: wx.BoxSizer) -> None:
		ayudante = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		datos = preferencias.seccion()
		self.posicion: wx.Choice = ayudante.addLabeledControl(
			# Translators: label of the choice of how cell positions are said, in the settings panel.
			_("Say the &position of the cells:"),
			wx.Choice,
			choices=[
				# Translators: option of how cell positions are said, in the settings panel.
				_("Long (Row 3, column 5)"),
				# Translators: option of how cell positions are said, in the settings panel.
				_("Short (R3C5)"),
			],
		)
		self.posicion.SetSelection(1 if datos["posicion_corta"] else 0)
		self.notas: wx.CheckBox = ayudante.addItem(
			wx.CheckBox(
				self,
				# Translators: check box in the settings panel.
				label=_("When writing a number, remove that &note from its row, column and block"),
			),
		)
		self.notas.SetValue(bool(datos["notas_automaticas"]))
		self.completados: wx.CheckBox = ayudante.addItem(
			# Translators: check box in the settings panel.
			wx.CheckBox(self, label=_("Announce when a row, column or block is &complete")),
		)
		self.completados.SetValue(bool(datos["anunciar_completados"]))
		self.sonidos: wx.CheckBox = ayudante.addItem(
			# Translators: check box in the settings panel.
			wx.CheckBox(self, label=_("Play s&ounds (complete groups, exercises, solved sudokus)")),
		)
		self.sonidos.SetValue(bool(datos["sonidos"]))
		borrar = ayudante.addItem(
			# Translators: button in the settings panel.
			wx.Button(self, label=_("&Delete my progress and statistics...")),
		)
		borrar.Bind(wx.EVT_BUTTON, self._al_borrar)

	def onSave(self) -> None:
		datos = preferencias.seccion()
		datos["posicion_corta"] = self.posicion.GetSelection() == 1
		datos["notas_automaticas"] = self.notas.GetValue()
		datos["anunciar_completados"] = self.completados.GetValue()
		datos["sonidos"] = self.sonidos.GetValue()
		preferencias.aplicar()

	def _al_borrar(self, evento: wx.CommandEvent) -> None:
		respuesta = MessageDialog.confirm(
			_(
				# Translators: asked before deleting the progress and statistics.
				"This deletes your progress in the course, your practice rounds, the days in a row "
				"and the statistics of your sudokus. Unfinished sudokus are kept. "
				"It cannot be undone. Delete them?",
			),
			# Translators: title of the confirmation to delete the progress.
			_("Delete my progress and statistics"),
			parent=self,
		)
		if respuesta != ReturnCode.OK:
			return
		borrar = type(self).al_borrar_progreso
		if borrar is not None and borrar():
			# Translators: reported after deleting the progress and statistics.
			ui.message(_("Your progress and statistics were deleted."))
