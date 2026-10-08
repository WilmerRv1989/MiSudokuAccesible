# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Escribe los ejercicios de técnicas de las lecciones a partir de su campo «generar».

Cada ejercicio con «generar»: {"objetivo": ..., "tamano": ..., "semilla": ...} (y «nivel» en los
sudokus enteros, con objetivo «completar») se genera con
`sudoku/curso/practica.py` y se escriben su tablero, su casilla, su instrucción y sus pistas
(en español, con las traducciones del archivo .po). Con la misma semilla sale siempre el mismo.

Uso (desde la raíz del repositorio, después de actualizar el .po):
	uv run python herramientas/preparar_lecciones.py
"""

import glob
import json
import os
import random
import sys

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_COMPLEMENTO = os.path.join(_RAIZ, "addon", "globalPlugins", "miSudokuAccesible")
sys.path.insert(0, _COMPLEMENTO)
sys.path.insert(0, os.path.join(_RAIZ, "tests", "unit"))

import po  # noqa: E402
from sudoku import idioma  # noqa: E402
from sudoku.curso.modelo import Ejercicio, Objetivo  # noqa: E402
from sudoku.generador import Nivel  # noqa: E402
from sudoku.curso.practica import generar_ejercicio  # noqa: E402
from sudoku.grupos import FORMAS  # noqa: E402

_PO_ES = os.path.join(_COMPLEMENTO, "..", "..", "locale", "es", "LC_MESSAGES", "nvda.po")


def _filas(tablero: tuple[int, ...], lado: int) -> list[str]:
	cifras = "".join(str(v) if v else "." for v in tablero)
	return [cifras[i : i + lado] for i in range(0, len(cifras), lado)]


def _casilla(indice: int, lado: int) -> list[int]:
	fila, columna = divmod(indice, lado)
	return [fila + 1, columna + 1]


def _datos(ejercicio: Ejercicio, generar: dict | None, lado: int) -> dict:
	"""El ejercicio como en el JSON. El segundo paso (sin `generar`) no lleva tablero: usa el del primero."""
	datos: dict = {"id": ejercicio.id}
	if generar is not None:
		datos["generar"] = generar
	datos["tipo"] = ejercicio.tipo.value
	if generar is not None:
		datos["tablero"] = _filas(ejercicio.tablero, lado)
	datos.update(
		{
			"objetivos": [_casilla(i, lado) for i in ejercicio.objetivos],
			"inicio": _casilla(ejercicio.inicio, lado),
			"instruccion": ejercicio.instruccion,
			"pistas": list(ejercicio.pistas),
		},
	)
	if ejercicio.orientacion:
		datos["orientacion"] = ejercicio.orientacion
	if ejercicio.notas:
		datos["notas"] = [[*_casilla(i, lado), "".join(map(str, numeros))] for i, numeros in ejercicio.notas]
	if ejercicio.quitar:
		datos["quitar"] = [[*_casilla(i, lado), numero] for i, numero in ejercicio.quitar]
	if ejercicio.segundo is not None:
		datos["segundo"] = _datos(ejercicio.segundo, None, lado)
	return datos


def main() -> None:
	idioma.configurar(*po.traducciones(os.path.normpath(_PO_ES)))
	for ruta in sorted(glob.glob(os.path.join(_COMPLEMENTO, "lecciones", "es", "bloque_*.json"))):
		with open(ruta, encoding="utf-8") as archivo:
			bloque = json.load(archivo)
		cambiados = 0
		for leccion in bloque["lecciones"]:
			for posicion, datos in enumerate(leccion["ejercicios"]):
				generar = datos.get("generar")
				if generar is None:
					continue
				forma = FORMAS[generar["tamano"]]
				ejercicio = generar_ejercicio(
					datos["id"],
					Objetivo(generar["objetivo"]),
					forma,
					random.Random(generar["semilla"]),
					Nivel(generar["nivel"]) if "nivel" in generar else None,
				)
				leccion["ejercicios"][posicion] = _datos(ejercicio, generar, forma.lado)
				cambiados += 1
		if cambiados:
			with open(ruta, "w", encoding="utf-8", newline="\n") as archivo:
				json.dump(bloque, archivo, ensure_ascii=False, indent=1)
				archivo.write("\n")
			print(f"{os.path.basename(ruta)}: {cambiados} ejercicios")


if __name__ == "__main__":
	main()
