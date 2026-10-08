# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Pruebas de lo que se dice de cada casilla, en español, con la traducción del archivo .po."""

import os
import sys
import unittest

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_COMPLEMENTO = os.path.join(_RAIZ, "addon", "globalPlugins", "miSudokuAccesible")
_PO_ES = os.path.join(_RAIZ, "addon", "locale", "es", "LC_MESSAGES", "nvda.po")
sys.path.insert(0, _COMPLEMENTO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import po  # noqa: E402
from sudoku import anunciador, idioma  # noqa: E402
from sudoku.generador import Nivel  # noqa: E402
from sudoku.grupos import CUATRO, NUEVE, SEIS, Grupo, TipoGrupo  # noqa: E402
from sudoku.tablero import ResultadoEscritura  # noqa: E402

FILA_3 = Grupo(TipoGrupo.FILA, 3)
BLOQUE_2 = Grupo(TipoGrupo.BLOQUE, 2)


class PruebaBloques(unittest.TestCase):
	def test_esquinas_y_centro(self) -> None:
		self.assertEqual(NUEVE.bloque(0, 0), 1)
		self.assertEqual(NUEVE.bloque(0, 8), 3)
		self.assertEqual(NUEVE.bloque(4, 4), 5)
		self.assertEqual(NUEVE.bloque(8, 0), 7)
		self.assertEqual(NUEVE.bloque(8, 8), 9)

	def test_bordes_de_bloque(self) -> None:
		self.assertEqual(NUEVE.bloque(2, 2), 1)
		self.assertEqual(NUEVE.bloque(2, 3), 2)
		self.assertEqual(NUEVE.bloque(3, 2), 4)

	def test_tableros_pequenos(self) -> None:
		# 6 por 6: bloques de 2 filas por 3 columnas, dos por fila de bloques.
		self.assertEqual(SEIS.bloque(0, 0), 1)
		self.assertEqual(SEIS.bloque(0, 3), 2)
		self.assertEqual(SEIS.bloque(2, 0), 3)
		self.assertEqual(SEIS.bloque(5, 5), 6)
		# 4 por 4: bloques de 2 por 2.
		self.assertEqual(CUATRO.bloque(1, 1), 1)
		self.assertEqual(CUATRO.bloque(1, 2), 2)
		self.assertEqual(CUATRO.bloque(3, 3), 4)
		for forma in (CUATRO, SEIS, NUEVE):
			for grupo in forma.todos:
				self.assertEqual(len(forma.indices_de(grupo)), forma.lado)
			for vecinas in forma.vecinas:
				# Las de su fila y su columna, más las de su bloque que no están en ninguna de las dos.
				otras_del_bloque = (forma.alto_bloque - 1) * (forma.ancho_bloque - 1)
				self.assertEqual(len(vecinas), 2 * (forma.lado - 1) + otras_del_bloque)

	def test_cada_bloque_tiene_nueve_casillas(self) -> None:
		cuenta: dict[int, int] = {}
		for fila in range(9):
			for columna in range(9):
				numero = NUEVE.bloque(fila, columna)
				cuenta[numero] = cuenta.get(numero, 0) + 1
		self.assertEqual(cuenta, {numero: 9 for numero in range(1, 10)})


class PruebaAnunciosEnEspanol(unittest.TestCase):
	def setUp(self) -> None:
		idioma.configurar(*po.traducciones(_PO_ES))

	def tearDown(self) -> None:
		idioma.configurar(idioma._sin_traduccion, idioma._plural_sin_traduccion)

	def test_casilla_vacia(self) -> None:
		self.assertEqual(anunciador.describir_casilla(2, 4), "Fila 3, columna 5, vacía")

	def test_casilla_al_cambiar_de_bloque(self) -> None:
		self.assertEqual(
			anunciador.describir_casilla(2, 4, bloque=2),
			"Fila 3, columna 5, vacía, bloque 2",
		)

	def test_casillas_con_numero_y_notas(self) -> None:
		self.assertEqual(anunciador.describir_casilla(2, 4, 7), "Fila 3, columna 5: 7")
		self.assertEqual(anunciador.describir_casilla(2, 4, 7, fija=True), "Fila 3, columna 5: 7, fija")
		self.assertEqual(
			anunciador.describir_casilla(2, 4, notas={7, 1, 4}, bloque=2),
			"Fila 3, columna 5, vacía, notas 1, 4 y 7, bloque 2",
		)
		self.assertEqual(anunciador.describir_notas({3}), "notas 3")
		self.assertEqual(anunciador.describir_notas(set()), "sin notas")

	def test_grupos(self) -> None:
		self.assertEqual(
			anunciador.describir_grupo(FILA_3, [7, 3, 5]),
			"Fila 3: tiene 3, 5 y 7; faltan 1, 2, 4, 6, 8 y 9",
		)
		self.assertEqual(anunciador.describir_grupo(BLOQUE_2, []), "Bloque 2: sin números")
		self.assertEqual(anunciador.describir_grupo(FILA_3, list(range(1, 10))), "Fila 3: completa")

	def test_escritura(self) -> None:
		self.assertEqual(anunciador.describir_escritura(7, ResultadoEscritura()), "7")
		choque = ResultadoEscritura(choques=[FILA_3, BLOQUE_2])
		self.assertEqual(
			anunciador.describir_escritura(5, choque),
			"5, choca con el 5 de la fila y del bloque",
		)
		completa = ResultadoEscritura(completados=[FILA_3, BLOQUE_2])
		self.assertEqual(
			anunciador.describir_escritura(9, completa),
			"9. Fila 3 completa. Bloque 2 completo",
		)

	def test_notas_y_borrado(self) -> None:
		self.assertEqual(anunciador.describir_nota(4, True), "nota 4 puesta")
		self.assertEqual(anunciador.describir_nota(4, False), "nota 4 quitada")
		self.assertEqual(anunciador.describir_borrado(7), "7 borrado")
		self.assertEqual(anunciador.describir_borrado(0), "notas borradas")
		self.assertEqual(anunciador.describir_borrado(None), "vacía")

	def test_estado(self) -> None:
		self.assertEqual(anunciador.describir_vacias(1), "Falta 1 casilla.")
		self.assertEqual(anunciador.describir_vacias(12), "Faltan 12 casillas.")
		self.assertEqual(
			anunciador.describir_comprobacion(0, 12),
			"Todo lo que escribiste está bien. Faltan 12 casillas.",
		)
		self.assertEqual(
			anunciador.describir_comprobacion(3, 12),
			"Hay 3 casillas mal. Faltan 12 casillas.",
		)
		self.assertEqual(anunciador.texto_tiempo(45), "45 segundos")
		self.assertEqual(anunciador.texto_tiempo(725), "12 minutos y 5 segundos")
		self.assertEqual(anunciador.texto_tiempo(3660), "1 hora y 1 minuto")
		self.assertEqual(
			anunciador.describir_resuelto(61),
			"¡Felicidades, resolviste el sudoku! Tiempo: 1 minuto y 1 segundo.",
		)
		self.assertEqual(anunciador.etiqueta_nivel(Nivel.DIFICIL), "Difícil")
		self.assertEqual(anunciador.etiqueta_tamano(4), "4 por 4")
		self.assertEqual(
			anunciador.describir_fuera_de_rango(4),
			"En este sudoku los números van del 1 al 4.",
		)
		self.assertEqual(
			anunciador.describir_grupo(Grupo(TipoGrupo.FILA, 2), [3, 1], 4),
			"Fila 2: tiene 1 y 3; faltan 2 y 4",
		)
		self.assertEqual(anunciador.describir_grupo(Grupo(TipoGrupo.FILA, 2), [4, 3, 1, 2], 4), "Fila 2: completa")


class PruebaTraduccion(unittest.TestCase):
	def test_todo_traducido(self) -> None:
		sin_traducir = [
			entrada.msgid
			for entrada in po.leer(_PO_ES)
			if entrada.msgid and (entrada.fuzzy or not all(entrada.msgstr.values()))
		]
		self.assertEqual(sin_traducir, [])


if __name__ == "__main__":
	unittest.main()
