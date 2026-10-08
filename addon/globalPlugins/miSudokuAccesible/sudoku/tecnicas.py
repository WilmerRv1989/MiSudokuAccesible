# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Resolutor «humano»: encuentra la siguiente jugada lógica, como la buscaría una persona.

No prueba números al azar: solo usa técnicas que se pueden explicar, de la más fácil a la más difícil.
Sirve para dar pistas y para medir la dificultad de un sudoku (la técnica más difícil que necesita).

Los «candidatos» de una casilla vacía son los números que todavía pueden ir en ella.
Las técnicas de colocación ponen un número; las de eliminación quitan candidatos,
y con eso aparece una colocación nueva.
"""

import enum
from dataclasses import dataclass, replace

from .grupos import Grupo, TipoGrupo, forma_de


class Tecnica(enum.IntEnum):
	"""Las técnicas, ordenadas de la más fácil a la más difícil."""

	# Colocaciones.
	ULTIMO_NUMERO = 1  # A un grupo solo le falta un número.
	UNICO_LUGAR = 2  # En un grupo, un número solo cabe en una casilla.
	UNICO_NUMERO = 3  # En una casilla solo cabe un número.
	# Eliminaciones.
	INTERSECCION = 4  # En un grupo, un número solo cabe donde se cruza con otro grupo.
	PAREJA = 5  # Dos casillas de un grupo se reparten dos números.


@dataclass(frozen=True)
class Eliminacion:
	"""Candidatos que se descartan con una intersección o una pareja.

	Intersección: en `grupo`, el número de `numeros` solo cabe en `casillas`, que están también en `otro`;
	por eso se descarta del resto de `otro`.
	Pareja: en `grupo`, las dos `casillas` se reparten los dos `numeros`. Si `oculta` es False,
	esas casillas solo admiten esos números, y se descartan del resto del grupo; si es True,
	esos números solo caben en esas casillas, y se descartan los demás números de esas casillas.
	"""

	tecnica: Tecnica
	grupo: Grupo
	numeros: tuple[int, ...]
	casillas: tuple[int, ...]
	quitados: tuple[tuple[int, int], ...]  # (casilla, número)
	otro: Grupo | None = None
	oculta: bool = False


@dataclass(frozen=True)
class Paso:
	"""Una jugada lógica: el número que va en una casilla, y por qué."""

	tecnica: Tecnica
	indice: int
	numero: int
	# El grupo que se mira (en «último número» y «único lugar»).
	grupo: Grupo | None = None
	# Lo que hubo que descartar antes de llegar a la colocación.
	eliminaciones: tuple[Eliminacion, ...] = ()

	@property
	def dificultad(self) -> Tecnica:
		return max([self.tecnica, *(e.tecnica for e in self.eliminaciones)])


class Resolutor:
	"""Lleva los números puestos y los candidatos de cada casilla vacía."""

	def __init__(self, valores: list[int]) -> None:
		self.valores = list(valores)
		self.forma = forma = forma_de(self.valores)
		self.candidatos: list[set[int]] = []
		for indice in range(forma.casillas):
			if self.valores[indice]:
				self.candidatos.append(set())
			else:
				usados = {self.valores[i] for i in forma.vecinas[indice]}
				self.candidatos.append(set(forma.numeros) - usados)

	def colocar(self, indice: int, numero: int) -> None:
		self.valores[indice] = numero
		self.candidatos[indice] = set()
		for i in self.forma.vecinas[indice]:
			self.candidatos[i].discard(numero)

	def resuelto(self) -> bool:
		return all(self.valores)

	# Colocaciones.

	def buscar_colocacion(self) -> tuple[Tecnica, int, int, Grupo | None] | None:
		for grupo in self.forma.todos:
			vacias = [i for i in self.forma.casillas_de[grupo] if not self.valores[i]]
			if len(vacias) == 1 and len(self.candidatos[vacias[0]]) == 1:
				return Tecnica.ULTIMO_NUMERO, vacias[0], next(iter(self.candidatos[vacias[0]])), grupo
		for grupo in self.forma.todos:
			casillas = self.forma.casillas_de[grupo]
			puestos = {self.valores[i] for i in casillas}
			for numero in self.forma.numeros:
				if numero in puestos:
					continue
				lugares = [i for i in casillas if numero in self.candidatos[i]]
				if len(lugares) == 1:
					return Tecnica.UNICO_LUGAR, lugares[0], numero, grupo
		for indice in range(self.forma.casillas):
			if len(self.candidatos[indice]) == 1:
				return Tecnica.UNICO_NUMERO, indice, next(iter(self.candidatos[indice])), None
		return None

	# Eliminaciones.

	def buscar_eliminacion(self) -> Eliminacion | None:
		return self._interseccion() or self._pareja()

	def aplicar(self, eliminacion: Eliminacion) -> None:
		for indice, numero in eliminacion.quitados:
			self.candidatos[indice].discard(numero)

	def _interseccion(self) -> Eliminacion | None:
		for grupo in self.forma.todos:
			for numero in self.forma.numeros:
				lugares = [i for i in self.forma.casillas_de[grupo] if numero in self.candidatos[i]]
				if len(lugares) < 2:
					continue
				# Los otros grupos que contienen todos esos lugares (una fila o columna dentro de un bloque,
				# o el bloque de una fila o columna).
				comunes = set(self.forma.grupos_de(lugares[0])) - {grupo}
				for i in lugares[1:]:
					comunes &= set(self.forma.grupos_de(i))
				for otro in sorted(comunes, key=lambda g: g.tipo.value):
					if (grupo.tipo is TipoGrupo.BLOQUE) == (otro.tipo is TipoGrupo.BLOQUE):
						continue
					quitados = tuple(
						(i, numero)
						for i in self.forma.casillas_de[otro]
						if i not in lugares and numero in self.candidatos[i]
					)
					if quitados:
						return Eliminacion(
							Tecnica.INTERSECCION,
							grupo,
							(numero,),
							tuple(lugares),
							quitados,
							otro=otro,
						)
		return None

	def _pareja(self) -> Eliminacion | None:
		for grupo in self.forma.todos:
			casillas = self.forma.casillas_de[grupo]
			vacias = [i for i in casillas if not self.valores[i]]
			# Pareja a la vista: dos casillas que solo admiten los mismos dos números.
			for posicion, a in enumerate(vacias):
				if len(self.candidatos[a]) != 2:
					continue
				for b in vacias[posicion + 1 :]:
					if self.candidatos[b] != self.candidatos[a]:
						continue
					numeros = tuple(sorted(self.candidatos[a]))
					quitados = tuple(
						(i, n) for i in vacias if i not in (a, b) for n in numeros if n in self.candidatos[i]
					)
					if quitados:
						return Eliminacion(Tecnica.PAREJA, grupo, numeros, (a, b), quitados)
			# Pareja oculta: dos números que solo caben en las mismas dos casillas.
			lugares = {n: tuple(i for i in vacias if n in self.candidatos[i]) for n in self.forma.numeros}
			dobles = [n for n in self.forma.numeros if len(lugares[n]) == 2]
			for posicion, n1 in enumerate(dobles):
				for n2 in dobles[posicion + 1 :]:
					if lugares[n1] != lugares[n2]:
						continue
					quitados = tuple(
						(i, n) for i in lugares[n1] for n in sorted(self.candidatos[i]) if n not in (n1, n2)
					)
					if quitados:
						return Eliminacion(
							Tecnica.PAREJA,
							grupo,
							(n1, n2),
							lugares[n1],
							quitados,
							oculta=True,
						)
		return None

	# Pasos.

	def siguiente_paso(self) -> Paso | None:
		"""La siguiente jugada lógica, o None si ninguna técnica sirve. Aplica las eliminaciones que use.

		Las eliminaciones se buscan en orden hasta que aparece una colocación; después se quitan
		de la explicación las que no hacían falta para llegar a ella.
		"""
		antes = [set(c) for c in self.candidatos]
		eliminaciones: list[Eliminacion] = []
		while True:
			colocacion = self.buscar_colocacion()
			if colocacion is not None:
				tecnica, indice, numero, grupo = colocacion
				paso = Paso(tecnica, indice, numero, grupo, tuple(eliminaciones))
				return self._podar(antes, paso) if eliminaciones else paso
			eliminacion = self.buscar_eliminacion()
			if eliminacion is None:
				return None
			self.aplicar(eliminacion)
			eliminaciones.append(eliminacion)

	# Poda de eliminaciones.

	def _sigue_valida(self, candidatos: list[set[int]], eliminacion: Eliminacion) -> bool:
		"""Si la razón de una eliminación se cumple con estos candidatos."""
		casillas = self.forma.casillas_de[eliminacion.grupo]
		if eliminacion.tecnica is Tecnica.INTERSECCION or eliminacion.oculta:
			# Los números solo pueden ir en las casillas de la intersección o de la pareja.
			return all(
				i in eliminacion.casillas for n in eliminacion.numeros for i in casillas if n in candidatos[i]
			)
		# Pareja a la vista: las dos casillas no admiten otros números.
		return all(candidatos[i] <= set(eliminacion.numeros) for i in eliminacion.casillas)

	def _coloca(self, candidatos: list[set[int]], paso: Paso) -> bool:
		"""Si con estos candidatos se llega a la colocación del paso, con su misma técnica."""
		indice, numero = paso.indice, paso.numero
		if numero not in candidatos[indice]:
			return False
		if paso.grupo is None:
			return len(candidatos[indice]) == 1
		return [i for i in self.forma.casillas_de[paso.grupo] if numero in candidatos[i]] == [indice]

	def _podar(self, antes: list[set[int]], paso: Paso) -> Paso:
		"""Quita una a una las eliminaciones que no hacen falta, comprobando que las demás siguen valiendo."""
		necesarias = list(paso.eliminaciones)
		for eliminacion in list(necesarias):
			prueba = [e for e in necesarias if e is not eliminacion]
			candidatos = [set(c) for c in antes]
			valida = True
			for e in prueba:
				if not self._sigue_valida(candidatos, e):
					valida = False
					break
				for i, n in e.quitados:
					candidatos[i].discard(n)
			if valida and self._coloca(candidatos, paso):
				necesarias = prueba
		return replace(paso, eliminaciones=tuple(necesarias))


def siguiente_paso(valores: list[int]) -> Paso | None:
	"""La siguiente jugada lógica desde un tablero (que no debe tener números equivocados)."""
	return Resolutor(valores).siguiente_paso()


def calificar(enunciado: list[int]) -> Tecnica | None:
	"""La técnica más difícil que hace falta para resolver el sudoku, o None si no basta con estas."""
	resolutor = Resolutor(enunciado)
	mas_dificil = Tecnica.ULTIMO_NUMERO
	while not resolutor.resuelto():
		paso = resolutor.siguiente_paso()
		if paso is None:
			return None
		mas_dificil = max(mas_dificil, paso.dificultad)
		resolutor.colocar(paso.indice, paso.numero)
	return mas_dificil
