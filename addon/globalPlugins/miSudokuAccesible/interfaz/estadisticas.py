# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""«Mis estadísticas»: un mensaje navegable de NVDA, con un título por sección (se salta con H)."""

import datetime
from html import escape

import addonHandler
import languageHandler
import ui

from ..sudoku.curso.modelo import cargar_curso, carpeta_de_idioma
from ..sudoku.curso.progreso import Progreso
from ..sudoku.estadisticas import Estadisticas, secciones
from . import archivos

addonHandler.initTranslation()


def html_estadisticas() -> str:
	partes = []
	for titulo, lineas in secciones(
		Estadisticas(archivos.ruta_estadisticas()),
		cargar_curso(carpeta_de_idioma(languageHandler.getLanguage())),
		Progreso(archivos.ruta_progreso()),
		datetime.date.today(),
	):
		elementos = "".join(f"<li>{escape(linea)}</li>" for linea in lineas)
		partes.append(f"<h2>{escape(titulo)}</h2><ul>{elementos}</ul>")
	return "".join(partes)


def mostrar() -> None:
	ui.browseableMessage(
		html_estadisticas(),
		# Translators: title of the statistics window.
		title=_("My statistics"),
		isHtml=True,
		closeButton=True,
		copyButton=True,
	)
