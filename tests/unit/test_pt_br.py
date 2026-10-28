# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Pruebas de la traducción al portugués de Brasil: el .po, los anuncios y el curso."""

import os
import re
import sys
import unittest

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_COMPLEMENTO = os.path.join(_RAIZ, "addon", "globalPlugins", "miSudokuAccesible")
_PO_ES = os.path.join(_RAIZ, "addon", "locale", "es", "LC_MESSAGES", "nvda.po")
_PO_PT_BR = os.path.join(_RAIZ, "addon", "locale", "pt_BR", "LC_MESSAGES", "nvda.po")
sys.path.insert(0, _COMPLEMENTO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import po  # noqa: E402
from sudoku import anunciador, idioma  # noqa: E402
from sudoku.curso.modelo import Ejercicio, carpeta_de_idioma, cargar_curso  # noqa: E402
from sudoku.generador import Nivel  # noqa: E402
from sudoku.grupos import Grupo, TipoGrupo  # noqa: E402

_MARCADOR = re.compile(r"\{\w+\}")


def _marcadores(texto: str) -> list[str]:
	return sorted(_MARCADOR.findall(texto))


class PruebaArchivoPo(unittest.TestCase):
	def test_mismos_mensajes_que_el_espanol(self) -> None:
		self.assertEqual(
			[entrada.msgid for entrada in po.leer(_PO_PT_BR)],
			[entrada.msgid for entrada in po.leer(_PO_ES)],
		)

	def test_todo_traducido(self) -> None:
		sin_traducir = [
			entrada.msgid
			for entrada in po.leer(_PO_PT_BR)
			if entrada.msgid and (entrada.fuzzy or not all(entrada.msgstr.values()))
		]
		self.assertEqual(sin_traducir, [])

	def test_marcadores_y_aceleradores(self) -> None:
		for entrada in po.leer(_PO_PT_BR):
			if not entrada.msgid:
				continue
			for indice, texto in entrada.msgstr.items():
				with self.subTest(msgid=entrada.msgid, forma=indice):
					origen = entrada.msgid_plural if indice and entrada.msgid_plural else entrada.msgid
					# Cada forma del plural puede escribir el número con letras en vez de {count}.
					if entrada.msgid_plural is None or "{count}" in texto:
						self.assertEqual(_marcadores(texto), _marcadores(origen))
					self.assertEqual(texto.count("&"), entrada.msgid.count("&"))


class PruebaAnunciosEnPortugues(unittest.TestCase):
	def setUp(self) -> None:
		idioma.configurar(*po.traducciones(_PO_PT_BR))

	def tearDown(self) -> None:
		idioma.configurar(idioma._sin_traduccion, idioma._plural_sin_traduccion)

	def test_casillas(self) -> None:
		self.assertEqual(anunciador.describir_casilla(2, 4), "Linha 3, coluna 5, vazia")
		self.assertEqual(anunciador.describir_casilla(2, 4, 7), "Linha 3, coluna 5: 7")
		self.assertEqual(anunciador.describir_casilla(2, 4, 7, fija=True), "Linha 3, coluna 5: 7, fixo")
		self.assertEqual(
			anunciador.describir_casilla(2, 4, notas={7, 1, 4}, bloque=2),
			"Linha 3, coluna 5, vazia, anotações 1, 4 e 7, bloco 2",
		)

	def test_grupos(self) -> None:
		fila_3 = Grupo(TipoGrupo.FILA, 3)
		self.assertEqual(
			anunciador.describir_grupo(fila_3, [7, 3, 5]),
			"Linha 3: tem 3, 5 e 7; faltam 1, 2, 4, 6, 8 e 9",
		)
		self.assertEqual(anunciador.describir_grupo(fila_3, list(range(1, 10))), "Linha 3: completo")

	def test_estado(self) -> None:
		self.assertEqual(anunciador.describir_vacias(1), "Falta 1 célula vazia.")
		self.assertEqual(anunciador.describir_vacias(12), "Faltam 12 células vazias.")
		self.assertEqual(anunciador.texto_tiempo(725), "12 minutos e 5 segundos")
		self.assertEqual(anunciador.texto_tiempo(3660), "1 hora e 1 minuto")
		self.assertEqual(anunciador.etiqueta_nivel(Nivel.DIFICIL), "Difícil")
		self.assertEqual(anunciador.etiqueta_tamano(4), "4 por 4")


class PruebaCursoEnPortugues(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.es = cargar_curso(os.path.join(_COMPLEMENTO, "lecciones", "es"))
		cls.pt = cargar_curso(os.path.join(_COMPLEMENTO, "lecciones", "pt_BR"))

	def test_se_elige_por_el_idioma_de_nvda(self) -> None:
		self.assertEqual(os.path.basename(carpeta_de_idioma("pt_BR")), "pt_BR")
		self.assertEqual(os.path.basename(carpeta_de_idioma("pt_PT")), "es")

	def test_misma_estructura_que_el_curso_en_espanol(self) -> None:
		def esqueleto(ejercicio: Ejercicio) -> tuple[object, ...]:
			return (
				ejercicio.id,
				ejercicio.tipo,
				ejercicio.tablero,
				ejercicio.objetivos,
				ejercicio.inicio,
				ejercicio.notas,
				ejercicio.quitar,
			)

		self.assertEqual(
			[(leccion.id, [esqueleto(e) for e in leccion.ejercicios], leccion.practica) for leccion in self.pt.lecciones],
			[(leccion.id, [esqueleto(e) for e in leccion.ejercicios], leccion.practica) for leccion in self.es.lecciones],
		)

	def test_todos_los_textos_estan_en_portugues(self) -> None:
		for bloque in self.pt.bloques:
			self.assertTrue(bloque.titulo and bloque.mensaje_final)
		for leccion in self.pt.lecciones:
			with self.subTest(leccion=leccion.id):
				self.assertTrue(leccion.titulo)
				self.assertTrue(all(leccion.explicacion))
				for ejercicio in leccion.ejercicios:
					self.assertTrue(ejercicio.instruccion)
		# Palabras del español que no existen en portugués: delatan un texto sin traducir.
		textos = [
			texto
			for leccion in self.pt.lecciones
			for texto in (
				*leccion.explicacion,
				*(e.instruccion for e in leccion.ejercicios),
				*(p for e in leccion.ejercicios for p in e.pistas),
			)
		]
		self.assertEqual([t for t in textos if re.search(r"\b(casilla|fila|pulsa|Mayúsculas)\w*|[¿¡ñ]", t)], [])


if __name__ == "__main__":
	unittest.main()
