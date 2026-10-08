# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Un sudoku en juego: números escritos, notas, choques, pistas, deshacer y guardado."""

import json
from dataclasses import dataclass, field

from .generador import Nivel
from . import tecnicas
from .grupos import Grupo, forma_de
from .tecnicas import Paso

_VERSION_GUARDADO = 1


@dataclass
class ResultadoEscritura:
	# Grupos donde ya estaba el número escrito.
	choques: list[Grupo] = field(default_factory=list)
	# Grupos que quedaron con sus 9 números distintos.
	completados: list[Grupo] = field(default_factory=list)
	resuelto: bool = False


@dataclass(frozen=True)
class Pista:
	"""Lo que dice una pista. Solo uno de estos casos a la vez:

	- `error`: casilla con un número equivocado (y cuántos más hay). Desde un error no se puede razonar.
	- `paso`: la siguiente jugada lógica.
	- `revelada`: ninguna técnica sirve (no pasa en los sudokus generados): se dice el número de una casilla.
	"""

	error: int | None = None
	otros_errores: int = 0
	paso: Paso | None = None
	revelada: int | None = None


class Sudoku:
	def __init__(self, enunciado: list[int], solucion: list[int], nivel: Nivel) -> None:
		self.enunciado = list(enunciado)
		self.solucion = list(solucion)
		self.nivel = nivel
		self.forma = forma_de(self.enunciado)
		self.valores = list(enunciado)
		self.notas: list[set[int]] = [set() for _ in range(self.forma.casillas)]
		# Segundos jugados (solo informativo).
		self.segundos = 0.0
		# Fecha (AAAA-MM-DD) si es el sudoku del día.
		self.del_dia: str | None = None
		# Sin ayudas: no hay pistas ni aviso de choques.
		self.ayudas = True
		# Cada cambio guarda cómo estaban las casillas que tocó: {índice: (valor, notas)}.
		self._historial: list[dict[int, tuple[int, frozenset[int]]]] = []

	# Consultas.

	def es_fija(self, indice: int) -> bool:
		return self.enunciado[indice] != 0

	def vacias(self) -> int:
		return sum(1 for valor in self.valores if not valor)

	@property
	def resuelto(self) -> bool:
		return self.valores == self.solucion

	@property
	def empezado(self) -> bool:
		"""Si hay algo escrito además del enunciado: números o notas."""
		return self.valores != self.enunciado or any(self.notas)

	def numeros_de(self, grupo: Grupo) -> list[int]:
		return [self.valores[i] for i in self.forma.indices_de(grupo) if self.valores[i]]

	def errores(self) -> int:
		"""Casillas escritas que no coinciden con la solución."""
		return sum(1 for v, s in zip(self.valores, self.solucion) if v and v != s)

	def pista(self) -> Pista | None:
		"""La pista para seguir desde el tablero actual, o None si el sudoku está resuelto."""
		if self.resuelto:
			return None
		errores = [i for i, (v, s) in enumerate(zip(self.valores, self.solucion)) if v and v != s]
		if errores:
			return Pista(error=errores[0], otros_errores=len(errores) - 1)
		paso = tecnicas.siguiente_paso(self.valores)
		if paso is not None:
			return Pista(paso=paso)
		return Pista(revelada=self.valores.index(0))

	def siguiente_vacia(self, indice: int, paso: int) -> int | None:
		"""La siguiente casilla vacía en orden de lectura (paso 1) o la anterior (paso -1), dando la vuelta."""
		casillas = self.forma.casillas
		for distancia in range(1, casillas + 1):
			candidata = (indice + paso * distancia) % casillas
			if not self.valores[candidata]:
				return candidata
		return None

	# Cambios.

	def _anotar(self, indices: list[int]) -> None:
		self._historial.append({i: (self.valores[i], frozenset(self.notas[i])) for i in indices})

	def escribir(self, indice: int, numero: int, quitar_notas: bool = True) -> ResultadoEscritura:
		"""Escribe un número en una casilla que no es fija. Con `quitar_notas`, quita esa nota
		de su fila, columna y bloque."""
		vecinas = sorted(self.forma.vecinas[indice])
		choques = [
			grupo
			for grupo in self.forma.grupos_de(indice)
			if any(self.valores[i] == numero for i in self.forma.indices_de(grupo) if i != indice)
		]
		con_nota = [i for i in vecinas if numero in self.notas[i]] if quitar_notas else []
		self._anotar([indice, *con_nota])
		self.valores[indice] = numero
		self.notas[indice].clear()
		for i in con_nota:
			self.notas[i].discard(numero)
		completados = [
			grupo
			for grupo in self.forma.grupos_de(indice)
			if len(set(self.numeros_de(grupo))) == self.forma.lado
		]
		return ResultadoEscritura(choques, completados, self.resuelto)

	def borrar(self, indice: int) -> int | None:
		"""Borra el número de la casilla o, si no tiene, sus notas. Devuelve el número borrado."""
		valor = self.valores[indice]
		if not valor and not self.notas[indice]:
			return None
		self._anotar([indice])
		if valor:
			self.valores[indice] = 0
			return valor
		self.notas[indice].clear()
		return 0

	def alternar_nota(self, indice: int, numero: int) -> bool:
		"""Pone o quita una nota en una casilla vacía. Devuelve True si quedó puesta."""
		self._anotar([indice])
		notas = self.notas[indice]
		if numero in notas:
			notas.discard(numero)
			return False
		notas.add(numero)
		return True

	def deshacer(self) -> int | None:
		"""Deshace el último cambio. Devuelve la casilla principal que cambió, o None si no hay nada."""
		if not self._historial:
			return None
		cambio = self._historial.pop()
		for i, (valor, notas) in cambio.items():
			self.valores[i] = valor
			self.notas[i] = set(notas)
		return next(iter(cambio))

	def reiniciar(self) -> None:
		"""Vuelve al enunciado, con el tiempo a cero. No se puede deshacer."""
		self.valores = list(self.enunciado)
		self.segundos = 0.0
		self.notas = [set() for _ in range(self.forma.casillas)]
		self._historial.clear()

	# Guardado.

	def a_json(self) -> str:
		return json.dumps(
			{
				"version": _VERSION_GUARDADO,
				"nivel": self.nivel.value,
				"enunciado": "".join(map(str, self.enunciado)),
				"solucion": "".join(map(str, self.solucion)),
				"valores": "".join(map(str, self.valores)),
				"notas": ["".join(map(str, sorted(n))) for n in self.notas],
				"segundos": round(self.segundos),
				"del_dia": self.del_dia,
				"ayudas": self.ayudas,
			},
		)

	@classmethod
	def desde_json(cls, texto: str) -> "Sudoku":
		"""Lee un sudoku guardado. Lanza ValueError si el archivo no es válido."""
		try:
			datos = json.loads(texto)
			sudoku = cls(_cifras(datos["enunciado"]), _cifras(datos["solucion"]), Nivel(datos["nivel"]))
			valores = _cifras(datos["valores"])
			notas = [set(_cifras(n)) for n in datos["notas"]]
			segundos = float(datos.get("segundos", 0))
			del_dia = datos.get("del_dia")
			ayudas = bool(datos.get("ayudas", True))
			if del_dia is not None and not isinstance(del_dia, str):
				raise TypeError(del_dia)
		except (KeyError, TypeError, ValueError) as error:
			raise ValueError("Sudoku guardado no válido") from error
		listas = (sudoku.enunciado, sudoku.solucion, valores, notas)
		forma = sudoku.forma
		if any(len(lista) != forma.casillas for lista in listas) or any(0 in n for n in notas):
			raise ValueError("Sudoku guardado no válido")
		cifras = [*sudoku.enunciado, *sudoku.solucion, *valores, *(n for nota in notas for n in nota)]
		if any(cifra > forma.lado for cifra in cifras):
			raise ValueError("Sudoku guardado no válido")
		if any(e and v != e for e, v in zip(sudoku.enunciado, valores)):
			raise ValueError("Sudoku guardado no válido")
		sudoku.valores = valores
		sudoku.notas = notas
		sudoku.segundos = segundos
		sudoku.del_dia = del_dia
		sudoku.ayudas = ayudas
		return sudoku


def _cifras(texto: str) -> list[int]:
	# Las notas de una casilla pueden estar vacías: la longitud de los tableros se comprueba aparte.
	if not isinstance(texto, str) or (texto and not texto.isdigit()):
		raise ValueError(texto)
	return [int(c) for c in texto]
