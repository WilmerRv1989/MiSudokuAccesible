# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Preferencias del complemento, guardadas en la configuración de NVDA (sección miSudokuAccesible)."""

import config

from ..sudoku import anunciador
from ..sudoku.generador import Nivel
from ..sudoku.grupos import FORMAS, NUEVE, Forma

SECCION = "miSudokuAccesible"
ESPECIFICACION = {
	# Lo último elegido en el diálogo de nuevo sudoku.
	"tamano": "integer(default=9, min=4, max=9)",
	"nivel": 'option("facil", "medio", "dificil", default="facil")',
	"ayudas": "boolean(default=True)",
	# Panel de opciones.
	"notas_automaticas": "boolean(default=True)",
	"anunciar_completados": "boolean(default=True)",
	"sonidos": "boolean(default=True)",
	"posicion_corta": "boolean(default=False)",
}


def registrar() -> None:
	config.conf.spec[SECCION] = ESPECIFICACION
	config.post_configProfileSwitch.register(aplicar)
	aplicar()


def quitar() -> None:
	config.post_configProfileSwitch.unregister(aplicar)


def seccion():
	return config.conf[SECCION]


def aplicar() -> None:
	"""Pasa a la lógica del sudoku las preferencias de anuncio."""
	anunciador.configurar(bool(seccion()["posicion_corta"]))


def notas_automaticas() -> bool:
	return bool(seccion()["notas_automaticas"])


def anunciar_completados() -> bool:
	return bool(seccion()["anunciar_completados"])


def sonidos_activados() -> bool:
	return bool(seccion()["sonidos"])


def forma_guardada() -> Forma:
	return FORMAS.get(int(config.conf[SECCION]["tamano"]), NUEVE)


def nivel_guardado() -> Nivel:
	try:
		return Nivel(config.conf[SECCION]["nivel"])
	except ValueError:
		return Nivel.FACIL


def ayudas_guardadas() -> bool:
	return bool(config.conf[SECCION]["ayudas"])


def guardar(forma: Forma, nivel: Nivel, ayudas: bool) -> None:
	config.conf[SECCION]["tamano"] = forma.lado
	config.conf[SECCION]["nivel"] = nivel.value
	config.conf[SECCION]["ayudas"] = ayudas
