# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Estadísticas: sudokus resueltos, mejores tiempos y los días seguidos del sudoku del día.

Se guardan en un archivo JSON. Un archivo dañado no impide jugar: se empieza de cero.
Las fechas se reciben como parámetro, para poder probarlo sin depender del día de hoy.
"""

import datetime
import json
import os

from . import anunciador
from .curso.modelo import Curso
from .curso.practica import TAMANO_RONDA
from .curso.progreso import Progreso
from .generador import Nivel
from .grupos import FORMAS
from .idioma import _, ngettext

VERSION = 1


def _clave(lado: int, nivel: Nivel) -> str:
	return f"{lado}-{nivel.value}"


class Estadisticas:
	def __init__(self, ruta: str) -> None:
		self.ruta = ruta
		# «9-facil» → {"total": resueltos, "sin_ayudas": de ellos, sin ayudas, "mejor": segundos del mejor tiempo}.
		self.resueltos: dict[str, dict[str, int]] = {}
		# Sudoku del día: última fecha resuelta, días seguidos, récord y total.
		self.ultimo_del_dia: str | None = None
		self.racha = 0
		self.record = 0
		self.total_del_dia = 0
		self.cargar()

	def cargar(self) -> None:
		try:
			with open(self.ruta, encoding="utf-8") as archivo:
				datos = json.load(archivo)
		except (OSError, ValueError):
			return
		if not isinstance(datos, dict) or datos.get("version") != VERSION:
			return
		try:
			self.resueltos = {
				str(k): {
					"total": int(v["total"]),
					"sin_ayudas": int(v.get("sin_ayudas", 0)),
					"mejor": int(v["mejor"]),
				}
				for k, v in datos.get("resueltos", {}).items()
			}
			diario = datos.get("del_dia", {})
			self.ultimo_del_dia = diario.get("ultimo")
			self.racha = int(diario.get("racha", 0))
			self.record = int(diario.get("record", 0))
			self.total_del_dia = int(diario.get("total", 0))
		except (AttributeError, KeyError, TypeError, ValueError):
			# Archivo dañado: se empieza de cero.
			self.resueltos, self.ultimo_del_dia, self.racha, self.record, self.total_del_dia = (
				{},
				None,
				0,
				0,
				0,
			)

	def guardar(self) -> None:
		os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
		temporal = self.ruta + ".tmp"
		datos = {
			"version": VERSION,
			"resueltos": self.resueltos,
			"del_dia": {
				"ultimo": self.ultimo_del_dia,
				"racha": self.racha,
				"record": self.record,
				"total": self.total_del_dia,
			},
		}
		with open(temporal, "w", encoding="utf-8") as archivo:
			json.dump(datos, archivo, ensure_ascii=False, indent=1)
		os.replace(temporal, self.ruta)

	def registrar_resuelto(self, lado: int, nivel: Nivel, segundos: float, ayudas: bool = True) -> bool:
		"""Anota un sudoku resuelto. Devuelve True si es el mejor tiempo de ese tamaño y nivel."""
		clave = _clave(lado, nivel)
		segundos = round(segundos)
		datos = self.resueltos.get(clave)
		if datos is None:
			self.resueltos[clave] = {"total": 1, "sin_ayudas": 0 if ayudas else 1, "mejor": segundos}
			return False
		datos["total"] += 1
		if not ayudas:
			datos["sin_ayudas"] += 1
		if segundos < datos["mejor"]:
			datos["mejor"] = segundos
			return True
		return False

	def racha_actual(self, hoy: datetime.date) -> int:
		"""Los días seguidos, si siguen vivos: el último resuelto fue hoy o ayer."""
		if self.ultimo_del_dia is None:
			return 0
		ultimo = datetime.date.fromisoformat(self.ultimo_del_dia)
		return self.racha if (hoy - ultimo).days <= 1 else 0

	def resuelto_hoy(self, hoy: datetime.date) -> bool:
		return self.ultimo_del_dia == hoy.isoformat()

	def registrar_del_dia(self, fecha: datetime.date) -> int:
		"""Anota el sudoku del día resuelto y devuelve los días seguidos."""
		if self.resuelto_hoy(fecha):
			return self.racha
		self.racha = self.racha_actual(fecha) + 1
		self.record = max(self.record, self.racha)
		self.total_del_dia += 1
		self.ultimo_del_dia = fecha.isoformat()
		return self.racha


def texto_racha(racha: int) -> str:
	return ngettext(
		# Translators: days in a row solving the sudoku of the day.
		"You have solved it {count} day in a row.",
		"You have solved it {count} days in a row.",
		racha,
	).format(
		count=racha,
	)


def secciones(
	estadisticas: Estadisticas,
	curso: Curso,
	progreso: Progreso,
	hoy: datetime.date,
) -> list[tuple[str, list[str]]]:
	"""Las secciones de «Mis estadísticas»: título y líneas de cada una."""
	resueltos = []
	for lado in sorted(FORMAS, reverse=True):
		for nivel in Nivel:
			datos = estadisticas.resueltos.get(_clave(lado, nivel))
			if datos is None:
				continue
			if datos["sin_ayudas"]:
				linea = ngettext(
					# Translators: a line of the statistics, as in "9 by 9, Hard: 5 solved, 2 without help. Best time: 20 minutes."
					"{size}, {level}: {count} solved, {without} without help. Best time: {time}.",
					"{size}, {level}: {count} solved, {without} without help. Best time: {time}.",
					datos["total"],
				)
			else:
				linea = ngettext(
					# Translators: a line of the statistics, as in "9 by 9, Easy: 3 solved. Best time: 12 minutes and 5 seconds."
					"{size}, {level}: {count} solved. Best time: {time}.",
					"{size}, {level}: {count} solved. Best time: {time}.",
					datos["total"],
				)
			resueltos.append(
				linea.format(
					size=anunciador.etiqueta_tamano(lado),
					level=anunciador.etiqueta_nivel(nivel),
					count=datos["total"],
					without=datos["sin_ayudas"],
					time=anunciador.texto_tiempo(datos["mejor"]),
				),
			)
	if not resueltos:
		# Translators: statistics when no sudoku has been solved yet.
		resueltos.append(_("You have not solved any sudoku yet."))
	del_dia = [
		# Translators: a line of the statistics about the sudoku of the day.
		_("Days in a row: {count}.").format(count=estadisticas.racha_actual(hoy)),
		ngettext(
			# Translators: a line of the statistics about the sudoku of the day.
			"Record: {count} day in a row.",
			"Record: {count} days in a row.",
			estadisticas.record,
		).format(count=estadisticas.record),
		# Translators: a line of the statistics about the sudoku of the day.
		_("Solved in total: {count}.").format(count=estadisticas.total_del_dia),
	]
	if estadisticas.resuelto_hoy(hoy):
		# Translators: a line of the statistics about the sudoku of the day.
		del_dia.append(_("Today's sudoku is already solved."))
	lecciones = curso.lecciones
	terminadas = sum(1 for leccion in lecciones if progreso.leccion_completada(leccion))
	estrellas = sum(progreso.estrellas_de(leccion) for leccion in lecciones)
	posibles = sum(leccion.estrellas_posibles for leccion in lecciones)
	aprender = [
		# Translators: a line of the statistics about the course.
		_("Lessons finished: {done} of {total}.").format(done=terminadas, total=len(lecciones)),
		# Translators: a line of the statistics about the course.
		_("Stars: {stars} of {total}.").format(stars=estrellas, total=posibles),
	]
	for leccion in lecciones:
		mejor = progreso.mejor_practica(leccion.id)
		if mejor is not None:
			aprender.append(
				# Translators: a line of the statistics, as in "Best practice in lesson 4, Last number: 13 of 15."
				_("Best practice in lesson {id}, {title}: {stars} of {total}.").format(
					id=leccion.id,
					title=leccion.titulo,
					stars=mejor,
					total=3 * TAMANO_RONDA,
				),
			)
	return [
		# Translators: heading of the statistics.
		(_("Sudokus solved"), resueltos),
		# Translators: heading of the statistics.
		(_("Sudoku of the day"), del_dia),
		# Translators: heading of the statistics.
		(_("Learn to play"), aprender),
	]
