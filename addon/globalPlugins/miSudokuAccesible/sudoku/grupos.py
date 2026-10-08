# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""La forma del tablero (9 por 9, 6 por 6 o 4 por 4): sus filas, columnas y bloques.

Un tablero es una lista de números, fila por fila; el 0 es una casilla vacía.
En un tablero de lado N van los números del 1 al N, y cada bloque tiene N casillas:
3 por 3 en el de 9, 2 filas por 3 columnas en el de 6, y 2 por 2 en el de 4.
Los bloques se numeran de izquierda a derecha y de arriba abajo.
"""

import enum
from dataclasses import dataclass


class TipoGrupo(enum.Enum):
	FILA = 0
	COLUMNA = 1
	BLOQUE = 2


@dataclass(frozen=True)
class Grupo:
	"""Una fila, una columna o un bloque. `numero` va de 1 al lado del tablero."""

	tipo: TipoGrupo
	numero: int


class Forma:
	"""Todo lo que depende del tamaño del tablero, calculado una sola vez."""

	def __init__(self, lado: int, alto_bloque: int, ancho_bloque: int) -> None:
		self.lado = lado
		self.alto_bloque = alto_bloque
		self.ancho_bloque = ancho_bloque
		self.casillas = lado * lado
		self.numeros = range(1, lado + 1)
		# Para cada casilla: su fila, su columna y su bloque (desde 0).
		self.posiciones = [self._posicion(i) for i in range(self.casillas)]
		# Primero los bloques, luego las filas y las columnas: el orden en que se buscan las pistas.
		self.todos = [
			Grupo(tipo, n)
			for tipo in (TipoGrupo.BLOQUE, TipoGrupo.FILA, TipoGrupo.COLUMNA)
			for n in self.numeros
		]
		self.casillas_de = {grupo: self._indices_de(grupo) for grupo in self.todos}
		# Las casillas que comparten fila, columna o bloque con cada casilla (sin contarla a ella).
		self.vecinas = [
			frozenset(i for grupo in self.grupos_de(indice) for i in self.casillas_de[grupo]) - {indice}
			for indice in range(self.casillas)
		]

	def _posicion(self, indice: int) -> tuple[int, int, int]:
		fila, columna = divmod(indice, self.lado)
		return fila, columna, self.bloque(fila, columna) - 1

	def bloque(self, fila: int, columna: int) -> int:
		"""Número del bloque (desde 1) de una casilla, con la fila y la columna desde 0."""
		bloques_por_fila = self.lado // self.ancho_bloque
		return (fila // self.alto_bloque) * bloques_por_fila + columna // self.ancho_bloque + 1

	def _indices_de(self, grupo: Grupo) -> list[int]:
		n = grupo.numero - 1
		if grupo.tipo is TipoGrupo.FILA:
			return [n * self.lado + c for c in range(self.lado)]
		if grupo.tipo is TipoGrupo.COLUMNA:
			return [f * self.lado + n for f in range(self.lado)]
		bloques_por_fila = self.lado // self.ancho_bloque
		fila0 = (n // bloques_por_fila) * self.alto_bloque
		columna0 = (n % bloques_por_fila) * self.ancho_bloque
		return [
			(fila0 + f) * self.lado + columna0 + c
			for f in range(self.alto_bloque)
			for c in range(self.ancho_bloque)
		]

	def indices_de(self, grupo: Grupo) -> list[int]:
		"""Las casillas de un grupo, en orden de lectura."""
		return self.casillas_de[grupo]

	def grupos_de(self, indice: int) -> list[Grupo]:
		"""La fila, la columna y el bloque de una casilla."""
		fila, columna, bloque = self.posiciones[indice]
		return [
			Grupo(TipoGrupo.FILA, fila + 1),
			Grupo(TipoGrupo.COLUMNA, columna + 1),
			Grupo(TipoGrupo.BLOQUE, bloque + 1),
		]

	def grupo_de(self, indice: int, tipo: TipoGrupo) -> Grupo:
		return self.grupos_de(indice)[tipo.value]


NUEVE = Forma(9, 3, 3)
SEIS = Forma(6, 2, 3)
CUATRO = Forma(4, 2, 2)
FORMAS = {forma.lado: forma for forma in (CUATRO, SEIS, NUEVE)}


def forma_de(tablero: list[int]) -> Forma:
	"""La forma de un tablero, por su número de casillas. Lanza ValueError si no es ninguna."""
	for forma in FORMAS.values():
		if forma.casillas == len(tablero):
			return forma
	raise ValueError(f"Tablero de {len(tablero)} casillas")
