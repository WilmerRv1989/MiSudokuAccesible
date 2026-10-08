# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Pruebas del resolutor «humano», de las pistas y de sus textos en español."""

import os
import random
import sys
import unittest

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PO_ES = os.path.join(_RAIZ, "addon", "locale", "es", "LC_MESSAGES", "nvda.po")
sys.path.insert(0, os.path.join(_RAIZ, "addon", "globalPlugins", "miSudokuAccesible"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import po  # noqa: E402
from sudoku import anunciador, generador, idioma, tecnicas  # noqa: E402
from sudoku.generador import Nivel  # noqa: E402
from sudoku.grupos import Grupo, TipoGrupo  # noqa: E402
from sudoku.tablero import Pista, Sudoku  # noqa: E402
from sudoku.tecnicas import Eliminacion, Paso, Tecnica  # noqa: E402

from test_sudoku import ENUNCIADO, SOLUCION  # noqa: E402

FILA_3 = Grupo(TipoGrupo.FILA, 3)
BLOQUE_1 = Grupo(TipoGrupo.BLOQUE, 1)
BLOQUE_4 = Grupo(TipoGrupo.BLOQUE, 4)
COLUMNA_6 = Grupo(TipoGrupo.COLUMNA, 6)


def indice(fila: int, columna: int) -> int:
	return (fila - 1) * 9 + columna - 1


class PruebaResolutor(unittest.TestCase):
	def test_cada_paso_coincide_con_la_solucion(self) -> None:
		for nivel in Nivel:
			for semilla in range(4):
				with self.subTest(nivel=nivel, semilla=semilla):
					enunciado, solucion = generador.generar(nivel, random.Random(semilla))
					resolutor = tecnicas.Resolutor(enunciado)
					usadas: set[Tecnica] = set()
					while not resolutor.resuelto():
						paso = resolutor.siguiente_paso()
						self.assertIsNotNone(paso)
						assert paso is not None
						self.assertEqual(paso.numero, solucion[paso.indice])
						usadas.add(paso.dificultad)
						resolutor.colocar(paso.indice, paso.numero)
					self.assertIn(nivel.tecnica if nivel is not Nivel.FACIL else max(usadas), usadas)

	def test_ultimo_numero(self) -> None:
		valores = list(SOLUCION)
		valores[indice(3, 4)] = 0
		paso = tecnicas.siguiente_paso(valores)
		assert paso is not None
		self.assertEqual(paso.tecnica, Tecnica.ULTIMO_NUMERO)
		self.assertEqual((paso.indice, paso.numero), (indice(3, 4), SOLUCION[indice(3, 4)]))

	def test_calificar_sudoku_conocido(self) -> None:
		self.assertEqual(tecnicas.calificar(ENUNCIADO), Tecnica.UNICO_LUGAR)
		self.assertIsNone(tecnicas.calificar([0] * 81))


class PruebaPista(unittest.TestCase):
	def test_primero_avisa_del_error(self) -> None:
		sudoku = Sudoku(ENUNCIADO, SOLUCION, Nivel.FACIL)
		sudoku.escribir(2, 2)  # Fila 1, columna 3: va el 4.
		sudoku.escribir(3, 1)  # Fila 1, columna 4: va el 6.
		pista = sudoku.pista()
		assert pista is not None
		self.assertEqual((pista.error, pista.otros_errores), (2, 1))

	def test_paso_y_resuelto(self) -> None:
		sudoku = Sudoku(ENUNCIADO, SOLUCION, Nivel.FACIL)
		pista = sudoku.pista()
		assert pista is not None and pista.paso is not None
		self.assertEqual(pista.paso.numero, SOLUCION[pista.paso.indice])
		sudoku.valores = list(SOLUCION)
		self.assertIsNone(sudoku.pista())

	def test_revelada_si_no_sirve_ninguna_tecnica(self) -> None:
		sudoku = Sudoku([0] * 81, SOLUCION, Nivel.DIFICIL)
		pista = sudoku.pista()
		assert pista is not None
		self.assertEqual(pista.revelada, 0)


class PruebaTextosDePistas(unittest.TestCase):
	def setUp(self) -> None:
		idioma.configurar(*po.traducciones(_PO_ES))

	def tearDown(self) -> None:
		idioma.configurar(idioma._sin_traduccion, idioma._plural_sin_traduccion)

	def decir(self, pista: Pista | None, completa: bool) -> str:
		return anunciador.describir_pista(pista, list(SOLUCION), list(SOLUCION), completa)

	def test_ultimo_numero(self) -> None:
		pista = Pista(paso=Paso(Tecnica.ULTIMO_NUMERO, indice(3, 4), 6, FILA_3))
		self.assertEqual(self.decir(pista, False), "Mira la fila 3: solo le falta un número.")
		self.assertEqual(
			self.decir(pista, True),
			"En la fila 3 solo falta el 6: va en la fila 3, columna 4.",
		)

	def test_unico_lugar(self) -> None:
		pista = Pista(paso=Paso(Tecnica.UNICO_LUGAR, indice(5, 2), 7, BLOQUE_4))
		self.assertEqual(
			self.decir(pista, False),
			"Mira el bloque 4: hay un número que solo cabe en un lugar.",
		)
		self.assertEqual(
			self.decir(pista, True),
			"En el bloque 4, el 7 solo cabe en la fila 5, columna 2: "
			"las demás casillas vacías ya tienen un 7 en su fila, su columna o su bloque.",
		)

	def test_unico_numero(self) -> None:
		pista = Pista(paso=Paso(Tecnica.UNICO_NUMERO, indice(2, 8), 4))
		self.assertEqual(
			self.decir(pista, False),
			"Mira la fila 2: hay una casilla donde solo cabe un número.",
		)
		self.assertEqual(
			self.decir(pista, True),
			"En la fila 2, columna 8 solo cabe el 4: los demás números ya están en su fila, su columna o su bloque.",
		)

	def test_interseccion(self) -> None:
		fila_1 = Grupo(TipoGrupo.FILA, 1)
		eliminacion = Eliminacion(
			Tecnica.INTERSECCION,
			BLOQUE_1,
			(5,),
			(indice(1, 2), indice(1, 3)),
			((indice(1, 7), 5),),
			otro=fila_1,
		)
		pista = Pista(paso=Paso(Tecnica.UNICO_NUMERO, indice(1, 7), 3, None, (eliminacion,)))
		self.assertEqual(
			self.decir(pista, False),
			"Puedes escribir un número en la fila 1, pero antes hace falta una intersección en el bloque 1.",
		)
		self.assertEqual(
			self.decir(pista, True),
			"El 3 va en la fila 1, columna 7. Por qué: "
			"En el bloque 1, el 5 solo puede ir en la fila 1, columna 2 y la fila 1, columna 3, "
			"que están también en la fila 1. Así que en la fila 1 no puede haber otro 5 fuera de esas casillas. "
			"Por eso, en la fila 1, columna 7 solo cabe el 3.",
		)

	def test_parejas(self) -> None:
		casillas = (indice(2, 6), indice(7, 6))
		pareja = Eliminacion(Tecnica.PAREJA, COLUMNA_6, (3, 8), casillas, ((indice(4, 6), 3),))
		pista = Pista(paso=Paso(Tecnica.UNICO_LUGAR, indice(4, 6), 5, COLUMNA_6, (pareja,)))
		self.assertEqual(
			self.decir(pista, False),
			"Puedes escribir un número en la columna 6, pero antes hace falta una pareja en la columna 6.",
		)
		self.assertEqual(
			self.decir(pista, True),
			"El 5 va en la fila 4, columna 6. Por qué: "
			"En la columna 6, la fila 2, columna 6 y la fila 7, columna 6 solo admiten el 3 y el 8. "
			"Así que en la columna 6 ninguna otra casilla puede tener un 3 ni un 8. "
			"Por eso, en la columna 6, el 5 solo cabe en la fila 4, columna 6.",
		)
		oculta = Eliminacion(Tecnica.PAREJA, COLUMNA_6, (3, 8), casillas, ((indice(2, 6), 1),), oculta=True)
		pista = Pista(paso=Paso(Tecnica.UNICO_NUMERO, indice(4, 6), 5, None, (oculta,)))
		self.assertEqual(
			self.decir(pista, True),
			"El 5 va en la fila 4, columna 6. Por qué: "
			"En la columna 6, el 3 y el 8 solo pueden ir en la fila 2, columna 6 y la fila 7, columna 6. "
			"Así que esas dos casillas no pueden tener otros números. "
			"Por eso, en la fila 4, columna 6 solo cabe el 5.",
		)

	def test_error_resuelto_y_revelada(self) -> None:
		valores = list(SOLUCION)
		valores[indice(3, 5)] = 4
		error = anunciador.describir_pista(Pista(error=indice(3, 5), otros_errores=2), valores, SOLUCION, False)
		self.assertEqual(
			error,
			"Antes de seguir, revisa la fila 3, columna 5: el 4 no es correcto. Hay 2 números equivocados más.",
		)
		self.assertEqual(self.decir(None, True), "El sudoku ya está resuelto.")
		self.assertEqual(
			self.decir(Pista(revelada=0), True),
			"Ninguna de las técnicas que conozco sirve aquí, así que te digo un número: en la fila 1, columna 1 va el 5.",
		)


if __name__ == "__main__":
	unittest.main()
