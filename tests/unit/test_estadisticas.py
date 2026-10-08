# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Pruebas del sudoku del día y de las estadísticas, con fechas fijas."""

import datetime
import os
import sys
import tempfile
import unittest

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_COMPLEMENTO = os.path.join(_RAIZ, "addon", "globalPlugins", "miSudokuAccesible")
_PO_ES = os.path.join(_RAIZ, "addon", "locale", "es", "LC_MESSAGES", "nvda.po")
sys.path.insert(0, _COMPLEMENTO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import po  # noqa: E402
from sudoku import diario, generador, idioma  # noqa: E402
from sudoku.curso.modelo import cargar_curso  # noqa: E402
from sudoku.curso.progreso import Progreso  # noqa: E402
from sudoku.estadisticas import Estadisticas, secciones  # noqa: E402
from sudoku.generador import Nivel  # noqa: E402
from sudoku.tablero import Sudoku  # noqa: E402

LUNES = datetime.date(2026, 10, 5)
DIA = datetime.timedelta(days=1)


class PruebaSudokuDelDia(unittest.TestCase):
	def test_nivel_segun_el_dia(self) -> None:
		niveles = [diario.nivel_del_dia(LUNES + i * DIA) for i in range(7)]
		F, M, D = Nivel.FACIL, Nivel.MEDIO, Nivel.DIFICIL
		self.assertEqual(niveles, [F, F, M, M, D, F, F])

	def test_mismo_dia_mismo_sudoku(self) -> None:
		primero = diario.sudoku_del_dia(LUNES)
		otra_vez = diario.sudoku_del_dia(LUNES)
		self.assertEqual(primero.enunciado, otra_vez.enunciado)
		self.assertNotEqual(primero.enunciado, diario.sudoku_del_dia(LUNES + DIA).enunciado)
		self.assertEqual(primero.del_dia, "2026-10-05")
		self.assertEqual(generador.contar_soluciones(primero.enunciado), 1)

	def test_guardado(self) -> None:
		sudoku = diario.sudoku_del_dia(LUNES, ayudas=False)
		cargado = Sudoku.desde_json(sudoku.a_json())
		self.assertEqual(cargado.del_dia, "2026-10-05")
		self.assertFalse(cargado.ayudas)
		normal = Sudoku(sudoku.enunciado, sudoku.solucion, Nivel.FACIL)
		cargado = Sudoku.desde_json(normal.a_json())
		self.assertIsNone(cargado.del_dia)
		self.assertTrue(cargado.ayudas)


class PruebaEstadisticas(unittest.TestCase):
	def setUp(self) -> None:
		self.carpeta = tempfile.TemporaryDirectory()
		self.ruta = os.path.join(self.carpeta.name, "estadisticas.json")

	def tearDown(self) -> None:
		self.carpeta.cleanup()

	def test_dias_seguidos(self) -> None:
		datos = Estadisticas(self.ruta)
		self.assertEqual(datos.racha_actual(LUNES), 0)
		self.assertEqual(datos.registrar_del_dia(LUNES), 1)
		# Resolverlo otra vez el mismo día no suma.
		self.assertEqual(datos.registrar_del_dia(LUNES), 1)
		self.assertEqual(datos.registrar_del_dia(LUNES + DIA), 2)
		self.assertEqual(datos.racha_actual(LUNES + 2 * DIA), 2)
		# Un día sin resolverlo corta la cuenta.
		self.assertEqual(datos.racha_actual(LUNES + 3 * DIA), 0)
		self.assertEqual(datos.registrar_del_dia(LUNES + 3 * DIA), 1)
		self.assertEqual((datos.record, datos.total_del_dia), (2, 3))
		self.assertTrue(datos.resuelto_hoy(LUNES + 3 * DIA))

	def test_mejores_tiempos_y_guardado(self) -> None:
		datos = Estadisticas(self.ruta)
		self.assertFalse(datos.registrar_resuelto(9, Nivel.FACIL, 600.4))
		self.assertTrue(datos.registrar_resuelto(9, Nivel.FACIL, 500))
		self.assertFalse(datos.registrar_resuelto(9, Nivel.FACIL, 700))
		datos.registrar_del_dia(LUNES)
		datos.guardar()
		cargadas = Estadisticas(self.ruta)
		self.assertEqual(cargadas.resueltos, {"9-facil": {"total": 3, "sin_ayudas": 0, "mejor": 500}})
		self.assertEqual(cargadas.racha_actual(LUNES), 1)

	def test_archivo_danado(self) -> None:
		with open(self.ruta, "w", encoding="utf-8") as archivo:
			archivo.write('{"version": 1, "resueltos": {"9-facil": "mal"}}')
		datos = Estadisticas(self.ruta)
		self.assertEqual((datos.resueltos, datos.racha), ({}, 0))

	def test_secciones_en_espanol(self) -> None:
		idioma.configurar(*po.traducciones(_PO_ES))
		try:
			datos = Estadisticas(self.ruta)
			datos.registrar_resuelto(9, Nivel.FACIL, 725)
			datos.registrar_resuelto(6, Nivel.MEDIO, 300, ayudas=False)
			datos.registrar_resuelto(6, Nivel.MEDIO, 400)
			datos.registrar_del_dia(LUNES)
			curso = cargar_curso(os.path.join(_COMPLEMENTO, "lecciones", "es"))
			progreso = Progreso(os.path.join(self.carpeta.name, "progreso.json"))
			progreso.registrar("1.1", 3)
			progreso.registrar_practica("4", 13)
			titulos, lineas = zip(*secciones(datos, curso, progreso, LUNES))
		finally:
			idioma.configurar(idioma._sin_traduccion, idioma._plural_sin_traduccion)
		self.assertEqual(titulos, ("Sudokus resueltos", "Sudoku del día", "Aprender a jugar"))
		self.assertEqual(
			lineas[0],
			[
				"9 por 9, Fácil: 1 resuelto. Mejor tiempo: 12 minutos y 5 segundos.",
				"6 por 6, Medio: 2 resueltos, 1 sin ayudas. Mejor tiempo: 5 minutos.",
			],
		)
		self.assertEqual(
			lineas[1],
			["Días seguidos: 1.", "Récord: 1 día seguido.", "Resueltos en total: 1.", "El sudoku de hoy ya está resuelto."],
		)
		self.assertIn("Mejor práctica en la lección 4, Último número: 13 de 15.", lineas[2])


if __name__ == "__main__":
	unittest.main()
