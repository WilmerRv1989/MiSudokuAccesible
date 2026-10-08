# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Pruebas del curso «Aprender a jugar»: las lecciones, los ejercicios y el progreso."""

import os
import random
import sys
import tempfile
import unittest

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_COMPLEMENTO = os.path.join(_RAIZ, "addon", "globalPlugins", "miSudokuAccesible")
_PO_ES = os.path.join(_RAIZ, "addon", "locale", "es", "LC_MESSAGES", "nvda.po")
sys.path.insert(0, _COMPLEMENTO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import po  # noqa: E402
from sudoku import generador, idioma, tecnicas  # noqa: E402
from sudoku.curso.modelo import Objetivo, TipoEjercicio, cargar_curso  # noqa: E402
from sudoku.curso.practica import generar_ejercicio  # noqa: E402
from sudoku.grupos import NUEVE, SEIS  # noqa: E402
from sudoku.curso.progreso import Progreso  # noqa: E402
from sudoku.curso.sesion import SesionEjercicio  # noqa: E402

CURSO = cargar_curso(os.path.join(_COMPLEMENTO, "lecciones", "es"))
EJERCICIOS = {e.id: e for leccion in CURSO.lecciones for e in leccion.ejercicios}


def casilla(fila: int, columna: int, lado: int = 4) -> int:
	return (fila - 1) * lado + columna - 1


class PruebaLecciones(unittest.TestCase):
	def test_ids_unicos(self) -> None:
		ids = [e.id for leccion in CURSO.lecciones for e in leccion.ejercicios]
		self.assertEqual(len(ids), len(set(ids)))
		self.assertEqual([leccion.id for leccion in CURSO.lecciones], [str(n) for n in range(1, 14)])
		# Solo las lecciones de técnicas (bloque B) tienen «Practicar».
		self.assertEqual(
			[leccion.practica is not None for leccion in CURSO.lecciones],
			[False] * 3 + [True] * 7 + [False] * 3,
		)

	def test_cada_ejercicio_tiene_sentido(self) -> None:
		for ejercicio in EJERCICIOS.values():
			with self.subTest(ejercicio=ejercicio.id):
				tablero = list(ejercicio.tablero)
				lado = round(len(tablero) ** 0.5)
				self.assertTrue(ejercicio.instruccion)
				self.assertIn(len(ejercicio.pistas), (0, 2))
				self.assertFalse(any(ejercicio.tablero[i] for i in ejercicio.objetivos))
				if ejercicio.tipo is TipoEjercicio.COMPLETAR:
					self.assertEqual(generador.contar_soluciones(tablero), 1)
					if not ejercicio.pistas:
						# Sin pistas escritas, las da el resolutor: tiene que poder resolverlo entero.
						self.assertIsNotNone(tecnicas.calificar(tablero))
				if ejercicio.tipo is TipoEjercicio.ESCRIBIR:
					# El número de cada casilla del ejercicio no puede ser otro.
					for i in ejercicio.objetivos:
						for otro in range(1, lado + 1):
							if otro != ejercicio.solucion[i]:
								prueba = tablero[:i] + [otro] + tablero[i + 1 :]
								self.assertEqual(generador.contar_soluciones(prueba, 1), 0)
				if ejercicio.tipo is TipoEjercicio.BORRAR:
					for i in ejercicio.objetivos:
						self.assertNotEqual(ejercicio.escritos[i], ejercicio.solucion[i])
				if ejercicio.tipo is TipoEjercicio.NOTAS:
					sesion = SesionEjercicio(ejercicio)
					for i in ejercicio.objetivos:
						self.assertGreaterEqual(len(sesion.candidatos(i)), 2)


class PruebaSesion(unittest.TestCase):
	def setUp(self) -> None:
		idioma.configurar(*po.traducciones(_PO_ES))

	def tearDown(self) -> None:
		idioma.configurar(idioma._sin_traduccion, idioma._plural_sin_traduccion)

	def test_escribir(self) -> None:
		sesion = SesionEjercicio(EJERCICIOS["1.1"])
		respuesta = sesion.escribir(casilla(2, 3), 1)
		self.assertTrue(respuesta.error)
		self.assertEqual(respuesta.mensaje, "En este ejercicio, escribe en la fila 1, columna 4.")
		respuesta = sesion.escribir(casilla(1, 4), 2)
		self.assertTrue(respuesta.error)
		self.assertEqual(respuesta.mensaje, "El 2 ya está en la fila 1. Prueba con otro.")
		self.assertEqual(sesion.sudoku.valores[casilla(1, 4)], 0)
		self.assertEqual(sesion.escribir(casilla(1, 1), 4).mensaje, "fija")
		respuesta = sesion.escribir(casilla(1, 4), 4)
		self.assertTrue(respuesta.aceptada and respuesta.superado)
		self.assertEqual(sesion.estrellas, 3)
		self.assertTrue(sesion.escribir(casilla(1, 4), 4).error)

	def test_estrellas_segun_pistas(self) -> None:
		sesion = SesionEjercicio(EJERCICIOS["1.2"])
		self.assertEqual(sesion.pista(False), "La columna 1 tiene el 1, el 2 y el 4. ¿Cuál falta?")
		self.assertEqual(sesion.estrellas, 2)
		sesion.pista(True)
		self.assertEqual(sesion.estrellas, 1)
		sesion.pista(False)
		self.assertEqual(sesion.estrellas, 1)

	def test_completar(self) -> None:
		ejercicio = EJERCICIOS["1.4"]
		sesion = SesionEjercicio(ejercicio)
		vacias = [i for i, v in enumerate(ejercicio.tablero) if not v]
		for i in vacias[:-1]:
			self.assertFalse(sesion.escribir(i, ejercicio.solucion[i]).superado)
		self.assertTrue(sesion.escribir(vacias[-1], ejercicio.solucion[vacias[-1]]).superado)

	def test_borrar(self) -> None:
		sesion = SesionEjercicio(EJERCICIOS["3.1"])
		self.assertTrue(sesion.escribir(casilla(1, 3), 3).error)
		self.assertEqual(sesion.borrar(casilla(1, 1)).mensaje, "fija")
		respuesta = sesion.borrar(casilla(1, 3))
		self.assertTrue(respuesta.superado)
		self.assertEqual(respuesta.mensaje, "4 borrado")

	def test_notas(self) -> None:
		sesion = SesionEjercicio(EJERCICIOS["3.2"])
		objetivo = casilla(2, 1)
		self.assertTrue(sesion.escribir(objetivo, 3).error)
		respuesta = sesion.alternar_nota(objetivo, 2)
		self.assertTrue(respuesta.error)
		self.assertEqual(respuesta.mensaje, "El 2 no puede ir aquí: ya está en el bloque 1.")
		self.assertTrue(sesion.alternar_nota(casilla(4, 4), 1).error)
		self.assertFalse(sesion.alternar_nota(objetivo, 3).superado)
		self.assertTrue(sesion.alternar_nota(objetivo, 4).superado)

	def test_ejercicio_de_tecnica_no_dice_la_casilla(self) -> None:
		ejercicio = EJERCICIOS["5.2"]
		sesion = SesionEjercicio(ejercicio)
		otra = next(i for i, v in enumerate(ejercicio.tablero) if not v and i not in ejercicio.objetivos)
		respuesta = sesion.escribir(otra, ejercicio.solucion[otra])
		self.assertTrue(respuesta.error)
		self.assertEqual(respuesta.mensaje, f"Aquí no. {ejercicio.orientacion}")
		self.assertTrue(ejercicio.orientacion.startswith("Mira el bloque"))
		objetivo = ejercicio.objetivos[0]
		self.assertTrue(sesion.escribir(objetivo, ejercicio.solucion[objetivo]).superado)

	def test_dos_pasos(self) -> None:
		ejercicio = EJERCICIOS["9.1"]
		sesion = SesionEjercicio(ejercicio)
		(indice, numero) = ejercicio.quitar[0]
		self.assertEqual(sesion.sudoku.notas[indice], set(dict(ejercicio.notas)[indice]))
		# En el paso 1 no se escribe ni se borra, y solo vale la nota que se descarta.
		self.assertTrue(sesion.escribir(indice, ejercicio.solucion[indice]).error)
		self.assertTrue(sesion.borrar(indice).error)
		otra = next(n for n in sesion.sudoku.notas[indice] if n != numero)
		respuesta = sesion.alternar_nota(indice, otra)
		self.assertTrue(respuesta.error)
		self.assertEqual(respuesta.mensaje, f"Esa no. {ejercicio.orientacion}")
		respuesta = sesion.alternar_nota(indice, numero)
		self.assertTrue(respuesta.nuevo_paso)
		self.assertFalse(respuesta.superado)
		self.assertTrue(respuesta.mensaje.endswith(ejercicio.segundo.instruccion))
		(objetivo,) = ejercicio.segundo.objetivos
		self.assertTrue(sesion.escribir(objetivo, ejercicio.solucion[objetivo]).superado)
		self.assertEqual(sesion.principal, ejercicio)

	def test_estrellas_de_un_sudoku_entero(self) -> None:
		ejercicio = EJERCICIOS["13.1"]
		self.assertIs(ejercicio.tipo, TipoEjercicio.COMPLETAR)
		self.assertEqual(round(len(ejercicio.tablero) ** 0.5), 9)
		sesion = SesionEjercicio(ejercicio)
		esperadas = [3, 3, 2, 2, 2, 1, 1]
		for pedidas, estrellas in enumerate(esperadas):
			self.assertEqual(sesion.estrellas, estrellas, f"{pedidas} pistas")
			sesion.pista(completa=True)

	def test_pista_del_resolutor(self) -> None:
		sesion = SesionEjercicio(EJERCICIOS["3.4"])
		self.assertTrue(sesion.pista(False).startswith("Mira "))


class PruebaPractica(unittest.TestCase):
	def test_cada_objetivo(self) -> None:
		for objetivo in Objetivo:
			forma = NUEVE if objetivo in (Objetivo.INTERSECCION, Objetivo.PAREJA) else SEIS
			with self.subTest(objetivo=objetivo):
				ejercicio = generar_ejercicio("p", objetivo, forma, random.Random(7))
				tablero = list(ejercicio.tablero)
				self.assertEqual(len(tablero), forma.casillas)
				if objetivo is Objetivo.COMPLETAR:
					# Un sudoku entero: sin pistas escritas, con una sola solución y resoluble con las técnicas.
					self.assertIs(ejercicio.tipo, TipoEjercicio.COMPLETAR)
					self.assertEqual(ejercicio.pistas, ())
					self.assertEqual(generador.contar_soluciones(tablero), 1)
					self.assertIsNotNone(tecnicas.calificar(tablero))
					continue
				self.assertEqual(len(ejercicio.pistas), 2)
				if objetivo is Objetivo.NOTAS:
					self.assertIs(ejercicio.tipo, TipoEjercicio.NOTAS)
					continue
				if objetivo in (Objetivo.INTERSECCION, Objetivo.PAREJA):
					self.comprobar_dos_pasos(ejercicio)
					continue
				(objetivo_casilla,) = ejercicio.objetivos
				self.assertEqual(tablero[objetivo_casilla], 0)
				self.assertTrue(ejercicio.orientacion)
				# El número de la casilla no puede ser otro.
				for otro in forma.numeros:
					if otro != ejercicio.solucion[objetivo_casilla]:
						prueba = tablero[:objetivo_casilla] + [otro] + tablero[objetivo_casilla + 1 :]
						self.assertEqual(generador.contar_soluciones(prueba, 1), 0)


	def comprobar_dos_pasos(self, ejercicio) -> None:
		"""Paso 1: quitar notas que están puestas y que no son la solución. Paso 2: escribir el número."""
		self.assertIs(ejercicio.tipo, TipoEjercicio.QUITAR_NOTAS)
		segundo = ejercicio.segundo
		self.assertIsNotNone(segundo)
		self.assertIs(segundo.tipo, TipoEjercicio.ESCRIBIR)
		self.assertTrue(ejercicio.instruccion.startswith("Step 1 of 2."))
		self.assertTrue(segundo.instruccion.startswith("Step 2 of 2."))
		notas = dict(ejercicio.notas)
		for indice, numero in ejercicio.quitar:
			self.assertIn(numero, notas[indice])
			self.assertNotEqual(ejercicio.solucion[indice], numero)
		sesion = SesionEjercicio(ejercicio)
		for indice, numero in ejercicio.quitar:
			respuesta = sesion.alternar_nota(indice, numero)
			self.assertFalse(respuesta.error)
		self.assertTrue(respuesta.nuevo_paso)
		self.assertIs(sesion.ejercicio, segundo)
		(objetivo,) = segundo.objetivos
		self.assertTrue(sesion.escribir(objetivo, ejercicio.solucion[objetivo]).superado)


class PruebaProgreso(unittest.TestCase):
	def test_guardar_y_cargar(self) -> None:
		with tempfile.TemporaryDirectory() as carpeta:
			ruta = os.path.join(carpeta, "progreso.json")
			progreso = Progreso(ruta)
			leccion = CURSO.lecciones[0]
			self.assertEqual(progreso.primer_pendiente(leccion), 0)
			progreso.registrar("1.1", 2)
			progreso.registrar("1.1", 1)
			progreso.registrar("1.2", 3)
			progreso.registrar_practica("4", 12)
			progreso.registrar_practica("4", 9)
			progreso.guardar()
			cargado = Progreso(ruta)
			self.assertEqual(cargado.estrellas_de(leccion), 5)
			self.assertEqual(cargado.primer_pendiente(leccion), 2)
			self.assertFalse(cargado.leccion_completada(leccion))
			self.assertEqual(cargado.mejor_practica("4"), 12)
			self.assertIsNone(cargado.mejor_practica("5"))

	def test_archivo_danado(self) -> None:
		with tempfile.TemporaryDirectory() as carpeta:
			ruta = os.path.join(carpeta, "progreso.json")
			with open(ruta, "w", encoding="utf-8") as archivo:
				archivo.write("{no es json")
			self.assertEqual(Progreso(ruta).ejercicios, {})


if __name__ == "__main__":
	unittest.main()
