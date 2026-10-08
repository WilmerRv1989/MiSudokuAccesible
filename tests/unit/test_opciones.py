# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Pruebas de las opciones, del guardado de las lecciones y de la lista de atajos (con NVDA simulado)."""

import builtins
import os
import re
import sys
import types
import unittest
from types import SimpleNamespace

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_COMPLEMENTO = os.path.join(_RAIZ, "addon", "globalPlugins", "miSudokuAccesible")
_PO_ES = os.path.join(_RAIZ, "addon", "locale", "es", "LC_MESSAGES", "nvda.po")
sys.path.insert(0, _COMPLEMENTO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import po  # noqa: E402
from sudoku import anunciador, idioma  # noqa: E402
from sudoku.curso.modelo import cargar_curso  # noqa: E402
from sudoku.curso.sesion import SesionEjercicio  # noqa: E402

from test_sudoku import nuevo  # noqa: E402

_gettext, _ngettext = po.traducciones(_PO_ES)


def _modulo(nombre: str, **atributos) -> types.ModuleType:
	modulo = types.ModuleType(nombre)
	modulo.__dict__.update(atributos)
	return modulo


def _instalar_traduccion() -> None:
	builtins._ = _gettext
	builtins.ngettext = _ngettext


# Simulación mínima de los módulos de NVDA que usa interfaz/atajos.py.
sys.modules.setdefault("addonHandler", _modulo("addonHandler", initTranslation=_instalar_traduccion))
sys.modules.setdefault("ui", _modulo("ui", browseableMessage=lambda *a, **k: None))
sys.modules.setdefault("logHandler", _modulo("logHandler", log=SimpleNamespace(debugWarning=lambda *a, **k: None)))
sys.modules.setdefault(
	"inputCore",
	_modulo(
		"inputCore",
		manager=SimpleNamespace(getAllGestureMappings=lambda obj, ancestors: {}),
		getDisplayTextForGestureIdentifier=lambda gesto: ("teclado", gesto.split(":", 1)[1]),
	),
)
_instalar_traduccion()

from interfaz import atajos  # noqa: E402

CURSO = cargar_curso(os.path.join(_COMPLEMENTO, "lecciones", "es"))
EJERCICIOS = {e.id: e for leccion in CURSO.lecciones for e in leccion.ejercicios}


def _ordenes(ruta: str) -> set[str]:
	with open(os.path.join(_COMPLEMENTO, "interfaz", ruta), encoding="utf-8") as archivo:
		return set(re.findall(r"def script_(\w+)\(", archivo.read()))


class PruebaFormaCorta(unittest.TestCase):
	def setUp(self) -> None:
		idioma.configurar(*po.traducciones(_PO_ES))

	def tearDown(self) -> None:
		anunciador.configurar(False)
		idioma.configurar(idioma._sin_traduccion, idioma._plural_sin_traduccion)

	def test_larga_y_corta(self) -> None:
		self.assertEqual(anunciador.describir_casilla(2, 4, 7, fija=True), "Fila 3, columna 5: 7, fija")
		anunciador.configurar(True)
		self.assertEqual(anunciador.describir_casilla(2, 4, 7, fija=True), "F3C5: 7, fija")
		self.assertEqual(anunciador.describir_casilla(2, 4), "F3C5, vacía")
		self.assertEqual(
			anunciador.describir_casilla(2, 4, notas={1, 4}, bloque=2),
			"F3C5, vacía, notas 1 y 4, bloque 2",
		)
		# Las pistas siguen diciendo la posición entera: van dentro de una frase.
		self.assertEqual(anunciador.posicion(22, 9), "la fila 3, columna 5")


class PruebaNotasAutomaticas(unittest.TestCase):
	def test_sin_quitar_notas(self) -> None:
		sudoku = nuevo()
		sudoku.alternar_nota(3, 4)
		sudoku.escribir(2, 4, quitar_notas=False)
		self.assertEqual(sudoku.notas[3], {4})


class PruebaLeccionEnCurso(unittest.TestCase):
	def test_continuar_un_sudoku_entero(self) -> None:
		ejercicio = EJERCICIOS["13.1"]
		sesion = SesionEjercicio(ejercicio)
		self.assertTrue(sesion.se_guarda)
		vacia = sesion.sudoku.valores.index(0)
		sesion.escribir(vacia, ejercicio.solucion[vacia])
		sesion.alternar_nota(sesion.sudoku.valores.index(0), ejercicio.solucion[sesion.sudoku.valores.index(0)])
		sesion.pista(completa=False)
		sesion.pista(completa=False)
		texto = sesion.a_json()
		otra = SesionEjercicio(ejercicio)
		self.assertTrue(otra.continuar(texto))
		self.assertTrue(otra.continuada)
		self.assertEqual(otra.sudoku.valores, sesion.sudoku.valores)
		self.assertEqual(otra.sudoku.notas, sesion.sudoku.notas)
		self.assertEqual(otra.estrellas, 2)
		# Otro ejercicio no recupera lo guardado.
		self.assertFalse(SesionEjercicio(EJERCICIOS["12.1"]).continuar(texto))
		self.assertFalse(SesionEjercicio(ejercicio).continuar("{no es json"))

	def test_solo_los_sudokus_enteros(self) -> None:
		self.assertFalse(SesionEjercicio(EJERCICIOS["5.2"]).se_guarda)


class PruebaAtajos(unittest.TestCase):
	def test_la_lista_tiene_todas_las_ordenes(self) -> None:
		del_tablero = _ordenes("tablero_sudoku.py")
		de_lecciones = _ordenes("tablero_leccion.py")
		globales = _ordenes(os.path.join("..", "__init__.py"))
		# En las lecciones, deshacer no se usa: la lista lo explica con una línea propia.
		en_lecciones = (del_tablero | de_lecciones) - {"deshacer"}
		for contexto, ordenes in ((atajos.Contexto.JUEGO, del_tablero), (atajos.Contexto.LECCION, en_lecciones)):
			en_la_lista = {
				orden
				for _titulo, entradas in atajos.secciones(contexto)
				for grupo, _fija, _descripcion in entradas
				if grupo is not None
				for orden in grupo
			}
			with self.subTest(contexto=contexto):
				self.assertLessEqual(ordenes, en_la_lista)
		_titulo, entradas = atajos._globales()
		self.assertEqual(globales, {orden for grupo, _f, _d in entradas if grupo for orden in grupo})

	def test_html_con_teclas_por_defecto(self) -> None:
		html = atajos.html_atajos({atajos.Contexto.JUEGO: object()})
		self.assertIn("<h2>Moverse por el tablero</h2>", html)
		self.assertIn("ninguna tecla asignada", html)


if __name__ == "__main__":
	unittest.main()
