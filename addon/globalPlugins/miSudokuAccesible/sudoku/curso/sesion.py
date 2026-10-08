# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Un ejercicio en curso: qué se acepta, qué se dice y cuándo está superado.

A diferencia del juego, en las lecciones un número equivocado no se escribe:
se explica por qué no va, para aprender sin tener que buscar el error después.
"""

import json
import random
from collections.abc import Callable
from dataclasses import dataclass, field

from .. import anunciador
from ..generador import Nivel
from ..grupos import Grupo
from ..idioma import _, ngettext
from ..tablero import Sudoku
from .modelo import Ejercicio, TipoEjercicio


@dataclass
class Respuesta:
	mensaje: str
	# Si el tablero cambió (hay que redibujarlo).
	aceptada: bool = False
	# Si suena el tono de error.
	error: bool = False
	# Grupos que se completaron (suena el sonido de completar).
	completados: list[Grupo] = field(default_factory=list)
	# Se terminó el primer paso y empieza el segundo (suena el sonido de éxito).
	nuevo_paso: bool = False
	superado: bool = False


def texto_animo(elegir: Callable[[list[str]], str] = random.choice) -> str:
	return elegir(
		[
			# Translators: praise when an exercise of the course is done.
			_("Very good!"),
			# Translators: praise when an exercise of the course is done.
			_("Excellent!"),
			# Translators: praise when an exercise of the course is done.
			_("You did it!"),
			# Translators: praise when an exercise of the course is done.
			_("Well done!"),
		],
	)


def texto_estrellas(estrellas: int) -> str:
	# Translators: stars earned in an exercise of the course.
	return ngettext("You earned {count} star.", "You earned {count} stars.", estrellas).format(
		count=estrellas,
	)


class SesionEjercicio:
	"""Un ejercicio, que puede tener dos pasos sobre el mismo tablero (quitar notas y escribir)."""

	def __init__(self, ejercicio: Ejercicio) -> None:
		# El ejercicio entero (su id cuenta para el progreso) y el paso en curso.
		self.principal = ejercicio
		self.ejercicio = ejercicio
		self.sudoku = Sudoku(list(ejercicio.tablero), list(ejercicio.solucion), Nivel.FACIL)
		for indice, valor in enumerate(ejercicio.escritos):
			if valor:
				self.sudoku.valores[indice] = valor
		for indice, numeros in ejercicio.notas:
			self.sudoku.notas[indice] = set(numeros)
		# 0: ninguna pista; 1: la breve; 2: la completa.
		self.pista_usada = 0
		# Pistas pedidas: en un sudoku entero, las estrellas dependen de cuántas.
		self.pistas_pedidas = 0
		self.superado = False
		# Si se continúa un sudoku entero que quedó a medias.
		self.continuada = False

	# Sudoku entero a medias.

	@property
	def se_guarda(self) -> bool:
		"""Solo se guarda a medias un sudoku entero: los demás ejercicios son cortos."""
		return self.principal.tipo is TipoEjercicio.COMPLETAR and not self.superado

	def a_json(self) -> str:
		return json.dumps(
			{"id": self.principal.id, "sudoku": self.sudoku.a_json(), "pistas": self.pistas_pedidas},
		)

	def continuar(self, texto: str) -> bool:
		"""Recupera el sudoku entero guardado, si es de este ejercicio. Devuelve True si lo recuperó."""
		try:
			datos = json.loads(texto)
			if datos["id"] != self.principal.id:
				return False
			guardado = Sudoku.desde_json(datos["sudoku"])
			pistas = int(datos["pistas"])
		except (KeyError, TypeError, ValueError):
			return False
		if guardado.enunciado != self.sudoku.enunciado:
			return False
		self.sudoku.valores = guardado.valores
		self.sudoku.notas = guardado.notas
		self.pistas_pedidas = pistas
		self.continuada = True
		return True

	@property
	def tipo(self) -> TipoEjercicio:
		return self.ejercicio.tipo

	@property
	def estrellas(self) -> int:
		"""3, 2 o 1. En un sudoku entero, según cuántas pistas (0 o 1, de 2 a 4, 5 o más);
		en los demás ejercicios, según la pista más completa que se usó."""
		if self.principal.tipo is TipoEjercicio.COMPLETAR and not self.principal.pistas:
			if self.pistas_pedidas <= 1:
				return 3
			return 2 if self.pistas_pedidas <= 4 else 1
		return 3 - self.pista_usada

	def candidatos(self, indice: int) -> set[int]:
		"""Los números que pueden ir en una casilla, según los que ya están puestos."""
		forma = self.sudoku.forma
		usados = {self.sudoku.valores[i] for i in forma.vecinas[indice]}
		return set(forma.numeros) - usados

	def _casillas(self, indices: list[int]) -> str:
		textos = [anunciador.posicion(i, self.sudoku.forma.lado) for i in indices]
		return anunciador.unir_textos(textos)

	def _pendientes(self) -> list[int]:
		return [i for i in self.ejercicio.objetivos if not self._objetivo_cumplido(i)]

	def _objetivo_cumplido(self, indice: int) -> bool:
		sudoku = self.sudoku
		if self.tipo is TipoEjercicio.ESCRIBIR:
			return sudoku.valores[indice] == sudoku.solucion[indice]
		if self.tipo is TipoEjercicio.NOTAS:
			return sudoku.notas[indice] == self.candidatos(indice)
		if self.tipo is TipoEjercicio.BORRAR:
			return sudoku.valores[indice] == 0
		return True

	def _paso_hecho(self) -> bool:
		if self.tipo is TipoEjercicio.COMPLETAR:
			return self.sudoku.resuelto
		if self.tipo is TipoEjercicio.QUITAR_NOTAS:
			return not any(numero in self.sudoku.notas[i] for i, numero in self.ejercicio.quitar)
		return not self._pendientes()

	def _cerrar_paso(self, respuesta: Respuesta) -> Respuesta:
		"""Si el paso está hecho, pasa al segundo o da el ejercicio por superado."""
		if not self._paso_hecho():
			return respuesta
		segundo = self.ejercicio.segundo
		if segundo is not None:
			self.ejercicio = segundo
			respuesta.mensaje = f"{respuesta.mensaje}. {texto_animo()} {segundo.instruccion}"
			respuesta.nuevo_paso = True
			return respuesta
		self.superado = respuesta.superado = True
		return respuesta

	def _ya_superado(self) -> Respuesta:
		# Translators: said when trying to change the board of an exercise that is already done.
		return Respuesta(_("This exercise is already done."), error=True)

	def _fija(self) -> Respuesta:
		# Translators: reported when trying to change a cell with a number from the puzzle.
		return Respuesta(_("fixed"), error=True)

	# Escribir.

	def escribir(self, indice: int, numero: int) -> Respuesta:
		sudoku = self.sudoku
		if self.superado:
			return self._ya_superado()
		if sudoku.es_fija(indice):
			return self._fija()
		if self.tipo is TipoEjercicio.NOTAS:
			# Translators: said when writing a number in an exercise about notes.
			mensaje = _("In this exercise you only write notes: press Shift and the number.")
			return Respuesta(mensaje, error=True)
		if self.tipo is TipoEjercicio.BORRAR:
			# Translators: said when writing a number in an exercise about deleting.
			mensaje = _("In this exercise you only delete: press Delete on the wrong number.")
			return Respuesta(mensaje, error=True)
		if self.tipo is TipoEjercicio.QUITAR_NOTAS:
			return self._solo_quitar_notas()
		if self.tipo is TipoEjercicio.ESCRIBIR and indice not in self.ejercicio.objetivos:
			if self.ejercicio.orientacion:
				# En los ejercicios de técnicas no se dice la casilla: encontrarla es el ejercicio.
				# Translators: said when writing in another cell in an exercise about a technique, as in "Not here. Look at the block 4: ..."
				mensaje = _("Not here. {orientation}").format(orientation=self.ejercicio.orientacion)
				return Respuesta(mensaje, error=True)
			# Translators: said when writing outside the cells of the exercise, as in "In this exercise, write in the row 1, column 4."
			mensaje = _("In this exercise, write in {cells}.").format(
				cells=self._casillas(self._pendientes()),
			)
			return Respuesta(mensaje, error=True)
		if sudoku.valores[indice] == numero:
			return Respuesta(str(numero))
		if numero != sudoku.solucion[indice]:
			return Respuesta(self._por_que_no(indice, numero), error=True)
		resultado = sudoku.escribir(indice, numero)
		respuesta = Respuesta(
			anunciador.describir_escritura(numero, resultado),
			aceptada=True,
			completados=resultado.completados,
		)
		return self._cerrar_paso(respuesta)

	def _solo_quitar_notas(self) -> Respuesta:
		# Translators: said when writing or deleting in the step where notes must be removed.
		mensaje = _("In this step you only remove notes: press Shift and the number of the note.")
		return Respuesta(mensaje, error=True)

	def _por_que_no(self, indice: int, numero: int) -> str:
		"""Por qué un número no va en una casilla: con qué choca, o que simplemente no es ese."""
		for grupo in self.sudoku.forma.grupos_de(indice):
			if any(
				self.sudoku.valores[i] == numero for i in self.sudoku.forma.indices_de(grupo) if i != indice
			):
				# Translators: said when a number is already in the row, column or block, as in "The 3 is already in the row 1. Try another one."
				return _("The {number} is already in {group}. Try another one.").format(
					number=numero,
					group=anunciador.grupo_en_frase(grupo),
				)
		# Translators: said when a number does not clash but is not the right one.
		return _("The {number} does not go here. Try another one.").format(number=numero)

	# Notas.

	def alternar_nota(self, indice: int, numero: int) -> Respuesta:
		sudoku = self.sudoku
		if self.superado:
			return self._ya_superado()
		if sudoku.es_fija(indice):
			return self._fija()
		if sudoku.valores[indice]:
			# Translators: reported when adding a note to a cell that already has a number.
			return Respuesta(_("The cell has a number. Delete it to write notes."), error=True)
		if self.tipo is TipoEjercicio.QUITAR_NOTAS:
			if (indice, numero) not in self.ejercicio.quitar or numero not in sudoku.notas[indice]:
				# Translators: said when touching another note in the step where notes must be removed, as in "Not that one. Remove note 7 from the row 3, column 7."
				mensaje = _("Not that one. {orientation}").format(orientation=self.ejercicio.orientacion)
				return Respuesta(mensaje, error=True)
		if self.tipo is TipoEjercicio.NOTAS:
			if indice not in self.ejercicio.objetivos:
				# Translators: said when writing notes outside the cells of the exercise.
				mensaje = _("In this exercise, write the notes in {cells}.").format(
					cells=self._casillas(self._pendientes()),
				)
				return Respuesta(mensaje, error=True)
			if numero not in self.candidatos(indice):
				return Respuesta(self._por_que_no_nota(indice, numero), error=True)
		puesta = sudoku.alternar_nota(indice, numero)
		respuesta = Respuesta(anunciador.describir_nota(numero, puesta), aceptada=True)
		if self.tipo in (TipoEjercicio.NOTAS, TipoEjercicio.QUITAR_NOTAS):
			return self._cerrar_paso(respuesta)
		return respuesta

	def _por_que_no_nota(self, indice: int, numero: int) -> str:
		for grupo in self.sudoku.forma.grupos_de(indice):
			if any(self.sudoku.valores[i] == numero for i in self.sudoku.forma.indices_de(grupo)):
				# Translators: said when a note cannot go in a cell, as in "The 2 cannot go here: it is already in the column 1."
				return _("The {number} cannot go here: it is already in {group}.").format(
					number=numero,
					group=anunciador.grupo_en_frase(grupo),
				)
		return _("The {number} does not go here. Try another one.").format(number=numero)

	# Borrar.

	def borrar(self, indice: int) -> Respuesta:
		sudoku = self.sudoku
		if self.superado:
			return self._ya_superado()
		if sudoku.es_fija(indice):
			return self._fija()
		if self.tipo is TipoEjercicio.QUITAR_NOTAS:
			return self._solo_quitar_notas()
		if (
			self.tipo is TipoEjercicio.BORRAR
			and sudoku.valores[indice]
			and indice not in self.ejercicio.objetivos
		):
			# Translators: said when deleting a right number in an exercise about deleting the wrong ones.
			return Respuesta(_("That number is right. Look for the wrong one."), error=True)
		borrado = sudoku.borrar(indice)
		respuesta = Respuesta(anunciador.describir_borrado(borrado), aceptada=borrado is not None)
		if self.tipo is TipoEjercicio.BORRAR:
			return self._cerrar_paso(respuesta)
		return respuesta

	# Pistas.

	def pista(self, completa: bool) -> str:
		self.pista_usada = max(self.pista_usada, 2 if completa else 1)
		self.pistas_pedidas += 1
		pistas = self.ejercicio.pistas
		if pistas:
			return pistas[-1] if completa else pistas[0]
		sudoku = self.sudoku
		return anunciador.describir_pista(sudoku.pista(), sudoku.valores, sudoku.solucion, completa)

	def texto_superado(self) -> str:
		return f"{texto_animo()} {texto_estrellas(self.estrellas)}"
