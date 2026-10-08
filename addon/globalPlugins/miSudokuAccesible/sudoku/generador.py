# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Generador de sudokus con una sola solución, y el resolutor que lo comprueba.

Cómo se genera un sudoku:
1. Se llena un tablero completo al azar (resolviendo uno vacío con los números en orden aleatorio).
2. Se quitan casillas por parejas simétricas respecto al centro, en orden aleatorio.
   Una pareja solo se quita si el sudoku sigue teniendo una sola solución y se puede resolver
   con las técnicas del nivel (ver tecnicas.py), sin bajar de las pistas mínimas del nivel.
3. Se mide qué técnica hace falta. Si no es la del nivel (un sudoku medio debe necesitar
   una intersección), se vuelve a empezar.
"""

import enum
import random

from . import tecnicas
from .grupos import NUEVE, Forma, forma_de
from .tecnicas import Tecnica

# Intentos antes de conformarse con el sudoku más cercano al nivel (casi nunca hacen falta tantos).
_INTENTOS = 200


class Nivel(enum.Enum):
	"""Los niveles se miden por la técnica más difícil que hace falta para resolver el sudoku."""

	FACIL = "facil"
	MEDIO = "medio"
	DIFICIL = "dificil"

	@property
	def tecnica(self) -> Tecnica:
		"""La técnica más difícil que puede necesitar un sudoku de este nivel."""
		return {
			Nivel.FACIL: Tecnica.UNICO_NUMERO,
			Nivel.MEDIO: Tecnica.INTERSECCION,
			Nivel.DIFICIL: Tecnica.PAREJA,
		}[self]

	def minimo_pistas(self, forma: Forma) -> int:
		"""Los sudokus fáciles conservan más números puestos (36 de 81), para empezar con más ayuda."""
		return round(forma.casillas * 36 / 81) if self is Nivel.FACIL else 0

	def admite(self, dificultad: Tecnica | None, forma: Forma = NUEVE) -> bool:
		"""Si un sudoku con esa dificultad es de este nivel.

		En los tableros pequeños casi nunca hacen falta las técnicas difíciles: el nivel medio
		solo se distingue del fácil por tener menos números puestos.
		"""
		if dificultad is None:
			return False
		if self is Nivel.FACIL or forma is not NUEVE:
			return dificultad <= self.tecnica
		return dificultad == self.tecnica


def niveles_de(forma: Forma) -> list[Nivel]:
	"""Los niveles que tienen sentido en cada tamaño: los tableros pequeños no tienen nivel difícil."""
	if forma is NUEVE:
		return list(Nivel)
	return [Nivel.FACIL, Nivel.MEDIO]


def contar_soluciones(tablero: list[int], limite: int = 2) -> int:
	"""Cuántas soluciones tiene el tablero, sin pasar de `limite` (para saber si es única)."""
	return _Resolutor(tablero).contar(limite)


def resolver(tablero: list[int], aleatorio: random.Random | None = None) -> list[int] | None:
	"""Una solución del tablero, o None si no tiene. Con `aleatorio`, prueba los números al azar."""
	return _Resolutor(tablero, aleatorio).primera()


class _Resolutor:
	"""Búsqueda con vuelta atrás: siempre sigue por la casilla con menos números posibles."""

	def __init__(self, tablero: list[int], aleatorio: random.Random | None = None) -> None:
		self.tablero = list(tablero)
		self.aleatorio = aleatorio
		self.forma = forma_de(self.tablero)
		lado = self.forma.lado
		# En cada fila, columna y bloque, los números usados como bits: el bit 0 es el 1.
		self.todos = (1 << lado) - 1
		self.filas = [0] * lado
		self.columnas = [0] * lado
		self.bloques = [0] * lado
		self.valido = True
		for indice, valor in enumerate(self.tablero):
			if valor:
				bit = 1 << (valor - 1)
				fila, columna, bloque = self.forma.posiciones[indice]
				if (self.filas[fila] | self.columnas[columna] | self.bloques[bloque]) & bit:
					self.valido = False
				self.filas[fila] |= bit
				self.columnas[columna] |= bit
				self.bloques[bloque] |= bit
		self.soluciones = 0
		self.limite = 1
		self.encontrada: list[int] | None = None

	def contar(self, limite: int) -> int:
		if not self.valido:
			return 0
		self.limite = limite
		self._buscar()
		return self.soluciones

	def primera(self) -> list[int] | None:
		if not self.valido:
			return None
		self.limite = 1
		self._buscar()
		return self.encontrada

	def _buscar(self) -> None:
		mejor = -1
		mejor_posibles = 0
		menos = self.forma.lado + 1
		for indice in range(self.forma.casillas):
			if self.tablero[indice]:
				continue
			fila, columna, bloque = self.forma.posiciones[indice]
			posibles = self.todos & ~(self.filas[fila] | self.columnas[columna] | self.bloques[bloque])
			cuantos = posibles.bit_count()
			if cuantos < menos:
				mejor, mejor_posibles, menos = indice, posibles, cuantos
				if cuantos <= 1:
					break
		if mejor < 0:
			self.soluciones += 1
			if self.encontrada is None:
				self.encontrada = list(self.tablero)
			return
		if menos == 0:
			return
		numeros = [n for n in self.forma.numeros if mejor_posibles & (1 << (n - 1))]
		if self.aleatorio is not None:
			self.aleatorio.shuffle(numeros)
		fila, columna, bloque = self.forma.posiciones[mejor]
		for numero in numeros:
			bit = 1 << (numero - 1)
			self.tablero[mejor] = numero
			self.filas[fila] |= bit
			self.columnas[columna] |= bit
			self.bloques[bloque] |= bit
			self._buscar()
			self.filas[fila] &= ~bit
			self.columnas[columna] &= ~bit
			self.bloques[bloque] &= ~bit
			self.tablero[mejor] = 0
			if self.soluciones >= self.limite:
				return


def generar(
	nivel: Nivel,
	aleatorio: random.Random | None = None,
	forma: Forma = NUEVE,
) -> tuple[list[int], list[int]]:
	"""Devuelve (enunciado, solución) de un sudoku nuevo del nivel y el tamaño pedidos."""
	aleatorio = aleatorio or random.Random()
	mejor: tuple[list[int], list[int]] | None = None
	mejor_dificultad = Tecnica.ULTIMO_NUMERO
	for _intento in range(_INTENTOS):
		solucion = resolver([0] * forma.casillas, aleatorio)
		assert solucion is not None
		enunciado = _quitar_casillas(solucion, nivel, aleatorio)
		dificultad = tecnicas.calificar(enunciado)
		if nivel.admite(dificultad, forma):
			return enunciado, solucion
		# Si no se llega al nivel, se queda el sudoku más difícil de los que se pueden resolver.
		if dificultad is not None and (mejor is None or dificultad > mejor_dificultad):
			mejor, mejor_dificultad = (enunciado, solucion), dificultad
	assert mejor is not None
	return mejor


def _quitar_casillas(solucion: list[int], nivel: Nivel, aleatorio: random.Random) -> list[int]:
	enunciado = list(solucion)
	casillas = len(enunciado)
	minimo = nivel.minimo_pistas(forma_de(enunciado))
	# Una casilla de cada pareja simétrica (en el tablero de 9, el centro es su propia pareja).
	orden = list(range((casillas + 1) // 2))
	aleatorio.shuffle(orden)
	quedan = casillas
	for indice in orden:
		pareja = {indice, casillas - 1 - indice}
		if quedan - len(pareja) < minimo:
			continue
		guardados = {i: enunciado[i] for i in pareja}
		for i in pareja:
			enunciado[i] = 0
		if contar_soluciones(enunciado) == 1 and _se_puede_resolver(enunciado, nivel):
			quedan -= len(pareja)
		else:
			for i, valor in guardados.items():
				enunciado[i] = valor
	return enunciado


def _se_puede_resolver(enunciado: list[int], nivel: Nivel) -> bool:
	dificultad = tecnicas.calificar(enunciado)
	return dificultad is not None and dificultad <= nivel.tecnica
