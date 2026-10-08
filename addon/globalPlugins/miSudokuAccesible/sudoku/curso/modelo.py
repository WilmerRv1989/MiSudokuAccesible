# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Bloques, lecciones y ejercicios del curso, leídos de los archivos JSON de `lecciones/<idioma>/`.

Cada archivo es un bloque. Un tablero se escribe como una lista de filas, con «.» en las casillas
vacías: ["12.4", "3412", ...]. Las casillas se escriben como [fila, columna], contando desde 1.

Los ejercicios de técnicas los escribe `herramientas/preparar_lecciones.py` a partir de su campo
«generar» (qué técnica practicar, tamaño y semilla); al cargar el curso, ese campo se ignora.
"""

import glob
import json
import os
from dataclasses import dataclass, replace
from enum import StrEnum

from .. import generador

CARPETA_LECCIONES = os.path.join(
	os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
	"lecciones",
)
IDIOMA_POR_DEFECTO = "es"


class TipoEjercicio(StrEnum):
	# Escribir el número que va en cada casilla de `objetivos`.
	ESCRIBIR = "escribir"
	# Llenar todas las casillas vacías.
	COMPLETAR = "completar"
	# Poner como notas, en cada casilla de `objetivos`, todos los números que pueden ir (y solo esos).
	NOTAS = "notas"
	# Borrar los números equivocados de las casillas de `objetivos`.
	BORRAR = "borrar"
	# Quitar las notas de `quitar`: es el descarte de una intersección o una pareja.
	QUITAR_NOTAS = "quitar_notas"


class Objetivo(StrEnum):
	"""Lo que practica un ejercicio generado (ver practica.py)."""

	ULTIMO_NUMERO = "ultimo_numero"
	UNICO_LUGAR_BLOQUE = "unico_lugar_bloque"
	UNICO_LUGAR_LINEA = "unico_lugar_linea"
	UNICO_NUMERO = "unico_numero"
	NOTAS = "notas"
	INTERSECCION = "interseccion"
	PAREJA = "pareja"
	# Un sudoku entero, para resolverlo de principio a fin.
	COMPLETAR = "completar"


@dataclass(frozen=True)
class Practica:
	"""«Practicar» de una lección: rondas de ejercicios nuevos de esa técnica."""

	objetivo: Objetivo
	lado: int


@dataclass(frozen=True)
class Ejercicio:
	id: str
	tipo: TipoEjercicio
	# Números del enunciado (fijos), fila por fila; 0 es una casilla vacía.
	tablero: tuple[int, ...]
	# Números ya escritos, como si los hubiera puesto la persona (pueden estar mal); 0 si no hay.
	escritos: tuple[int, ...]
	solucion: tuple[int, ...]
	objetivos: tuple[int, ...]
	# Casilla donde empieza el cursor.
	inicio: int
	instruccion: str
	# Pista breve y pista completa. Si no hay, las da el resolutor.
	pistas: tuple[str, ...]
	# En los ejercicios de técnicas: dónde mirar, sin decir la casilla. Se dice al escribir en otra.
	orientacion: str = ""
	# Notas ya puestas al empezar: (casilla, números).
	notas: tuple[tuple[int, tuple[int, ...]], ...] = ()
	# En QUITAR_NOTAS, las notas que hay que quitar: (casilla, número).
	quitar: tuple[tuple[int, int], ...] = ()
	# Segundo paso del ejercicio, sobre el mismo tablero (tras quitar las notas, escribir el número).
	segundo: "Ejercicio | None" = None


@dataclass(frozen=True)
class Leccion:
	id: str
	titulo: str
	explicacion: tuple[str, ...]
	ejercicios: tuple[Ejercicio, ...]
	practica: Practica | None = None

	@property
	def estrellas_posibles(self) -> int:
		return 3 * len(self.ejercicios)


@dataclass(frozen=True)
class Bloque:
	id: str
	titulo: str
	mensaje_final: str
	lecciones: tuple[Leccion, ...]


class Curso:
	def __init__(self, bloques: list[Bloque]) -> None:
		self.bloques = bloques
		self.lecciones = [leccion for bloque in bloques for leccion in bloque.lecciones]

	def bloque_de(self, leccion: Leccion) -> Bloque:
		return next(bloque for bloque in self.bloques if leccion in bloque.lecciones)

	def siguiente(self, leccion: Leccion) -> Leccion | None:
		indice = self.lecciones.index(leccion)
		return self.lecciones[indice + 1] if indice + 1 < len(self.lecciones) else None


def _tablero(filas: list[str]) -> list[int]:
	lado = len(filas)
	if any(len(fila) != lado for fila in filas):
		raise ValueError(f"Tablero no cuadrado: {filas}")
	return [0 if c == "." else int(c) for fila in filas for c in fila]


def _casilla(posicion: list[int], lado: int) -> int:
	fila, columna = posicion
	if not (1 <= fila <= lado and 1 <= columna <= lado):
		raise ValueError(f"Casilla fuera del tablero: {posicion}")
	return (fila - 1) * lado + columna - 1


def _ejercicio(datos: dict, padre: Ejercicio | None = None) -> Ejercicio:
	"""Un ejercicio. El segundo paso (`padre` dado) usa el tablero y la solución del primero."""
	if padre is not None:
		tablero, escritos, solucion = list(padre.tablero), list(padre.escritos), list(padre.solucion)
		lado = round(len(tablero) ** 0.5)
	else:
		tablero = _tablero(datos["tablero"])
		lado = len(datos["tablero"])
		escritos = _tablero(datos["escritos"]) if "escritos" in datos else [0] * len(tablero)
		if len(escritos) != len(tablero):
			raise ValueError(f"Ejercicio {datos['id']}: «escritos» no tiene el tamaño del tablero")
		resuelto = generador.resolver(tablero)
		if resuelto is None:
			raise ValueError(f"Ejercicio {datos['id']}: el tablero no tiene solución")
		solucion = resuelto
	ejercicio = Ejercicio(
		id=datos["id"],
		tipo=TipoEjercicio(datos["tipo"]),
		tablero=tuple(tablero),
		escritos=tuple(escritos),
		solucion=tuple(solucion),
		objetivos=tuple(_casilla(p, lado) for p in datos.get("objetivos", [])),
		inicio=_casilla(datos.get("inicio", [1, 1]), lado),
		instruccion=datos["instruccion"],
		pistas=tuple(datos.get("pistas", [])),
		orientacion=datos.get("orientacion", ""),
		notas=tuple(
			(_casilla([f, c], lado), tuple(int(n) for n in numeros))
			for f, c, numeros in datos.get("notas", [])
		),
		quitar=tuple((_casilla([f, c], lado), int(n)) for f, c, n in datos.get("quitar", [])),
	)
	if "segundo" in datos:
		ejercicio = replace(ejercicio, segundo=_ejercicio(datos["segundo"], ejercicio))
	return ejercicio


def _leccion(datos: dict) -> Leccion:
	practica = datos.get("practica")
	return Leccion(
		id=datos["id"],
		titulo=datos["titulo"],
		explicacion=tuple(datos["explicacion"]),
		ejercicios=tuple(_ejercicio(e) for e in datos["ejercicios"]),
		practica=Practica(Objetivo(practica["objetivo"]), int(practica["tamano"])) if practica else None,
	)


def carpeta_de_idioma(idioma: str) -> str:
	"""La carpeta de lecciones del idioma, o la del idioma por defecto si no existe."""
	for codigo in (idioma, idioma.split("_")[0], IDIOMA_POR_DEFECTO):
		carpeta = os.path.join(CARPETA_LECCIONES, codigo)
		if os.path.isdir(carpeta):
			return carpeta
	return os.path.join(CARPETA_LECCIONES, IDIOMA_POR_DEFECTO)


def cargar_curso(carpeta: str) -> Curso:
	bloques = []
	for ruta in sorted(glob.glob(os.path.join(carpeta, "bloque_*.json"))):
		with open(ruta, encoding="utf-8") as archivo:
			datos = json.load(archivo)
		bloques.append(
			Bloque(
				id=datos["id"],
				titulo=datos["titulo"],
				mensaje_final=datos["mensaje_final"],
				lecciones=tuple(_leccion(leccion) for leccion in datos["lecciones"]),
			),
		)
	return Curso(bloques)
