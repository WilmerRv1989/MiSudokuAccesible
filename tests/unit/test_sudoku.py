# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Pruebas del generador y del sudoku en juego: escribir, notas, choques, deshacer y guardado."""

import json
import os
import random
import sys
import time
import unittest

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_RAIZ, "addon", "globalPlugins", "miSudokuAccesible"))

from sudoku import generador, tecnicas  # noqa: E402
from sudoku.generador import Nivel  # noqa: E402
from sudoku.grupos import CUATRO, NUEVE, SEIS, Grupo, TipoGrupo  # noqa: E402
from sudoku.tablero import Sudoku  # noqa: E402

# Un sudoku conocido con una sola solución (fila por fila; 0 es vacía).
ENUNCIADO = [
	int(c)
	for c in (
		"530070000"
		"600195000"
		"098000060"
		"800060003"
		"400803001"
		"700020006"
		"060000280"
		"000419005"
		"000080079"
	)
]
SOLUCION = [
	int(c)
	for c in (
		"534678912"
		"672195348"
		"198342567"
		"859761423"
		"426853791"
		"713924856"
		"961537284"
		"287419635"
		"345286179"
	)
]


def nuevo() -> Sudoku:
	return Sudoku(ENUNCIADO, SOLUCION, Nivel.FACIL)


class PruebaGenerador(unittest.TestCase):
	def test_resolutor(self) -> None:
		self.assertEqual(generador.resolver(ENUNCIADO), SOLUCION)
		self.assertEqual(generador.contar_soluciones(ENUNCIADO), 1)
		self.assertEqual(generador.contar_soluciones([0] * 81), 2)

	def test_tablero_imposible(self) -> None:
		imposible = list(ENUNCIADO)
		imposible[2] = 5  # Otro 5 en la fila 1.
		self.assertEqual(generador.contar_soluciones(imposible), 0)
		self.assertIsNone(generador.resolver(imposible))

	def test_cada_nivel_tiene_solucion_unica(self) -> None:
		for nivel in Nivel:
			for semilla in range(5):
				with self.subTest(nivel=nivel, semilla=semilla):
					inicio = time.perf_counter()
					enunciado, solucion = generador.generar(nivel, random.Random(semilla))
					self.assertLess(time.perf_counter() - inicio, 5)
					self.assertEqual(generador.contar_soluciones(enunciado), 1)
					self.assertEqual(generador.resolver(enunciado), solucion)
					self.assertTrue(nivel.admite(tecnicas.calificar(enunciado)))
					self.assertGreaterEqual(sum(1 for v in enunciado if v), nivel.minimo_pistas(NUEVE))
					for i, valor in enumerate(enunciado):
						self.assertIn(valor, (0, solucion[i]))

	def test_solucion_valida(self) -> None:
		_enunciado, solucion = generador.generar(Nivel.MEDIO, random.Random(7))
		for tipo in TipoGrupo:
			for numero in range(1, 10):
				valores = {solucion[i] for i in NUEVE.indices_de(Grupo(tipo, numero))}
				self.assertEqual(valores, set(range(1, 10)))


class PruebaTablerosPequenos(unittest.TestCase):
	def test_generar(self) -> None:
		for forma in (CUATRO, SEIS):
			for nivel in generador.niveles_de(forma):
				for semilla in range(5):
					with self.subTest(lado=forma.lado, nivel=nivel, semilla=semilla):
						enunciado, solucion = generador.generar(nivel, random.Random(semilla), forma)
						self.assertEqual(len(enunciado), forma.casillas)
						self.assertEqual(generador.contar_soluciones(enunciado), 1)
						self.assertTrue(nivel.admite(tecnicas.calificar(enunciado), forma))
						self.assertGreaterEqual(sum(1 for v in enunciado if v), nivel.minimo_pistas(forma))
						for grupo in forma.todos:
							valores = {solucion[i] for i in forma.indices_de(grupo)}
							self.assertEqual(valores, set(forma.numeros))

	def test_niveles(self) -> None:
		self.assertEqual(generador.niveles_de(NUEVE), list(Nivel))
		self.assertEqual(generador.niveles_de(CUATRO), [Nivel.FACIL, Nivel.MEDIO])

	def test_jugar_y_guardar_un_cuatro_por_cuatro(self) -> None:
		enunciado, solucion = generador.generar(Nivel.FACIL, random.Random(3), CUATRO)
		sudoku = Sudoku(enunciado, solucion, Nivel.FACIL)
		self.assertIs(sudoku.forma, CUATRO)
		for i, valor in enumerate(solucion):
			if not sudoku.valores[i]:
				resultado = sudoku.escribir(i, valor)
		self.assertTrue(resultado.resuelto)
		cargado = Sudoku.desde_json(sudoku.a_json())
		self.assertIs(cargado.forma, CUATRO)
		self.assertEqual(cargado.valores, solucion)

	def test_numero_demasiado_alto_en_el_guardado(self) -> None:
		enunciado, solucion = generador.generar(Nivel.FACIL, random.Random(3), CUATRO)
		datos = json.loads(Sudoku(enunciado, solucion, Nivel.FACIL).a_json())
		# Un 9 en un tablero de 4 por 4.
		datos["solucion"] = "9" + datos["solucion"][1:]
		with self.assertRaises(ValueError):
			Sudoku.desde_json(json.dumps(datos))


class PruebaGrupos(unittest.TestCase):
	def test_indices(self) -> None:
		self.assertEqual(NUEVE.indices_de(Grupo(TipoGrupo.FILA, 2)), list(range(9, 18)))
		self.assertEqual(NUEVE.indices_de(Grupo(TipoGrupo.COLUMNA, 1)), list(range(0, 81, 9)))
		self.assertEqual(NUEVE.indices_de(Grupo(TipoGrupo.BLOQUE, 5)), [30, 31, 32, 39, 40, 41, 48, 49, 50])


class PruebaJuego(unittest.TestCase):
	def test_escribir_y_choques(self) -> None:
		sudoku = nuevo()
		# Fila 1, columna 3: un 5 choca con el 5 de la fila y del bloque.
		resultado = sudoku.escribir(2, 5)
		self.assertEqual(
			resultado.choques,
			[Grupo(TipoGrupo.FILA, 1), Grupo(TipoGrupo.BLOQUE, 1)],
		)
		resultado = sudoku.escribir(2, 4)
		self.assertEqual(resultado.choques, [])
		self.assertEqual(sudoku.valores[2], 4)
		self.assertEqual(sudoku.errores(), 0)
		sudoku.escribir(2, 2)
		self.assertEqual(sudoku.errores(), 1)

	def test_escribir_quita_notas_vecinas(self) -> None:
		sudoku = nuevo()
		sudoku.alternar_nota(2, 4)
		sudoku.alternar_nota(3, 4)  # Misma fila.
		sudoku.alternar_nota(20, 4)  # Mismo bloque.
		sudoku.alternar_nota(80, 4)  # Ni fila, ni columna, ni bloque.
		sudoku.alternar_nota(3, 6)
		sudoku.escribir(2, 4)
		self.assertEqual(sudoku.notas[2], set())
		self.assertEqual(sudoku.notas[3], {6})
		self.assertEqual(sudoku.notas[20], set())
		self.assertEqual(sudoku.notas[80], {4})
		# Deshacer devuelve el número y todas las notas.
		self.assertEqual(sudoku.deshacer(), 2)
		self.assertEqual(sudoku.valores[2], 0)
		self.assertEqual(sudoku.notas[2], {4})
		self.assertEqual(sudoku.notas[3], {4, 6})
		self.assertEqual(sudoku.notas[20], {4})

	def test_notas_y_borrar(self) -> None:
		sudoku = nuevo()
		self.assertTrue(sudoku.alternar_nota(2, 1))
		self.assertTrue(sudoku.alternar_nota(2, 4))
		self.assertFalse(sudoku.alternar_nota(2, 1))
		self.assertEqual(sudoku.notas[2], {4})
		self.assertEqual(sudoku.borrar(2), 0)
		self.assertEqual(sudoku.notas[2], set())
		self.assertIsNone(sudoku.borrar(2))
		sudoku.escribir(2, 4)
		self.assertEqual(sudoku.borrar(2), 4)
		self.assertEqual(sudoku.valores[2], 0)

	def test_deshacer_sin_cambios(self) -> None:
		self.assertIsNone(nuevo().deshacer())

	def test_completar_y_resolver(self) -> None:
		sudoku = nuevo()
		vacias = [i for i, v in enumerate(ENUNCIADO) if not v]
		self.assertEqual(sudoku.vacias(), len(vacias))
		# La fila 1 se completa con su última casilla.
		fila1 = [i for i in vacias if i < 9]
		for i in fila1[:-1]:
			self.assertEqual(sudoku.escribir(i, SOLUCION[i]).completados, [])
		resultado = sudoku.escribir(fila1[-1], SOLUCION[fila1[-1]])
		self.assertIn(Grupo(TipoGrupo.FILA, 1), resultado.completados)
		for i in vacias:
			if not sudoku.valores[i]:
				resultado = sudoku.escribir(i, SOLUCION[i])
		self.assertTrue(resultado.resuelto)
		self.assertTrue(sudoku.resuelto)
		self.assertEqual(sudoku.vacias(), 0)

	def test_siguiente_vacia(self) -> None:
		sudoku = nuevo()
		self.assertEqual(sudoku.siguiente_vacia(0, 1), 2)
		# Hacia atrás desde la casilla 2 da la vuelta: la 80 y la 79 tienen número, la 78 está vacía.
		self.assertEqual(sudoku.siguiente_vacia(2, -1), 78)
		self.assertEqual(sudoku.siguiente_vacia(80, 1), 2)

	def test_reiniciar(self) -> None:
		sudoku = nuevo()
		self.assertFalse(sudoku.empezado)
		sudoku.escribir(2, 4)
		sudoku.alternar_nota(3, 6)
		sudoku.segundos = 30
		self.assertTrue(sudoku.empezado)
		sudoku.reiniciar()
		self.assertFalse(sudoku.empezado)
		self.assertEqual(sudoku.segundos, 0)
		self.assertIsNone(sudoku.deshacer())


class PruebaGuardado(unittest.TestCase):
	def test_ida_y_vuelta(self) -> None:
		sudoku = nuevo()
		sudoku.escribir(2, 4)
		sudoku.alternar_nota(3, 6)
		sudoku.alternar_nota(3, 2)
		sudoku.segundos = 125.4
		cargado = Sudoku.desde_json(sudoku.a_json())
		self.assertEqual(cargado.enunciado, ENUNCIADO)
		self.assertEqual(cargado.solucion, SOLUCION)
		self.assertEqual(cargado.valores, sudoku.valores)
		self.assertEqual(cargado.notas, sudoku.notas)
		self.assertEqual(cargado.nivel, Nivel.FACIL)
		self.assertEqual(cargado.segundos, 125)

	def test_archivo_no_valido(self) -> None:
		for texto in ("", "{}", "[1, 2]", '{"nivel": "facil"}', nuevo().a_json().replace("530070000", "53007000")):
			with self.subTest(texto=texto[:30]):
				with self.assertRaises(ValueError):
					Sudoku.desde_json(texto)

	def test_no_se_cambia_el_enunciado(self) -> None:
		texto = nuevo().a_json().replace('"valores": "53', '"valores": "93')
		with self.assertRaises(ValueError):
			Sudoku.desde_json(texto)


if __name__ == "__main__":
	unittest.main()
