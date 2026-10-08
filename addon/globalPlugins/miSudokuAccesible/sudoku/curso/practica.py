# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Ejercicios generados: un tablero a medio resolver donde la siguiente jugada usa la técnica buscada.

Cómo se busca: se genera un sudoku y se resuelve paso a paso con el resolutor de las pistas.
Cada vez que la siguiente jugada es de la técnica buscada, ese momento sirve como ejercicio;
se elige uno al azar. El resolutor se crea de nuevo en cada paso, desde los números puestos,
para que la jugada coincida con la que se explica.

«Único lugar en filas y columnas» y «único número» casi nunca son la primera jugada del resolutor
(antes mira los bloques), así que para esas dos se buscan todas sus jugadas en cada momento,
quitando las que también se resuelven mirando solo el bloque.

Lo usan «Practicar» (en el momento) y `herramientas/preparar_lecciones.py` (para las lecciones).
"""

import random
from dataclasses import dataclass

from .. import anunciador, generador, tecnicas
from ..generador import Nivel
from ..grupos import Forma, TipoGrupo
from ..idioma import _, ngettext
from ..tecnicas import Paso, Tecnica
from .modelo import Ejercicio, Objetivo, TipoEjercicio

# Ejercicios de cada ronda de práctica.
TAMANO_RONDA = 5
# Sudokus que se prueban antes de rendirse (no debería pasar).
_SUDOKUS = 60

_NIVEL = {
	Objetivo.INTERSECCION: Nivel.MEDIO,
	Objetivo.PAREJA: Nivel.DIFICIL,
}


def _cumple(objetivo: Objetivo, paso: Paso) -> bool:
	if objetivo in (Objetivo.INTERSECCION, Objetivo.PAREJA):
		# Una sola eliminación, de la técnica que se practica: la explicación queda corta y clara.
		tecnica = Tecnica.INTERSECCION if objetivo is Objetivo.INTERSECCION else Tecnica.PAREJA
		return len(paso.eliminaciones) == 1 and paso.eliminaciones[0].tecnica is tecnica
	if paso.eliminaciones:
		return False
	if objetivo is Objetivo.ULTIMO_NUMERO:
		return paso.tecnica is Tecnica.ULTIMO_NUMERO
	if objetivo is Objetivo.UNICO_NUMERO:
		return paso.tecnica is Tecnica.UNICO_NUMERO
	if paso.tecnica is not Tecnica.UNICO_LUGAR or paso.grupo is None:
		return False
	en_bloque = paso.grupo.tipo is TipoGrupo.BLOQUE
	return en_bloque if objetivo is Objetivo.UNICO_LUGAR_BLOQUE else not en_bloque


@dataclass
class _Momento:
	valores: list[int]
	paso: Paso


def _momentos(enunciado: list[int]) -> list[_Momento]:
	"""Cada estado del tablero al resolverlo, con su siguiente jugada lógica."""
	valores = list(enunciado)
	momentos = []
	while not all(valores):
		paso = tecnicas.siguiente_paso(valores)
		if paso is None:
			break
		momentos.append(_Momento(list(valores), paso))
		valores[paso.indice] = paso.numero
	return momentos


def _colocaciones(valores: list[int], objetivo: Objetivo) -> list[Paso]:
	"""Todas las jugadas de «único lugar en una fila o columna» o de «único número» en un momento,
	sin las que también son «único lugar» en su bloque (esas se aprenden en otra lección)."""
	resolutor = tecnicas.Resolutor(valores)
	forma = resolutor.forma
	candidatos = resolutor.candidatos

	def lugares(numero: int, indices: list[int]) -> list[int]:
		return [i for i in indices if numero in candidatos[i]]

	def unico_en_bloque(indice: int, numero: int) -> bool:
		bloque = forma.grupo_de(indice, TipoGrupo.BLOQUE)
		return len(lugares(numero, forma.indices_de(bloque))) == 1

	pasos = []
	if objetivo is Objetivo.UNICO_NUMERO:
		for indice in range(forma.casillas):
			if len(candidatos[indice]) != 1:
				continue
			numero = next(iter(candidatos[indice]))
			if not any(len(lugares(numero, forma.indices_de(g))) == 1 for g in forma.grupos_de(indice)):
				pasos.append(Paso(Tecnica.UNICO_NUMERO, indice, numero))
		return pasos
	for grupo in forma.todos:
		if grupo.tipo is TipoGrupo.BLOQUE:
			continue
		indices = forma.indices_de(grupo)
		if sum(1 for i in indices if not valores[i]) < 2:
			continue
		for numero in forma.numeros:
			sitio = lugares(numero, indices)
			if len(sitio) == 1 and not unico_en_bloque(sitio[0], numero):
				pasos.append(Paso(Tecnica.UNICO_LUGAR, sitio[0], numero, grupo))
	return pasos


def generar_ejercicio(
	id_ejercicio: str,
	objetivo: Objetivo,
	forma: Forma,
	aleatorio: random.Random,
	nivel: Nivel | None = None,
) -> Ejercicio:
	"""Un ejercicio nuevo que practica `objetivo`. Lanza RuntimeError si no lo encuentra.

	`nivel` solo cuenta para un sudoku entero (COMPLETAR); en las técnicas lo decide la técnica.
	"""
	if objetivo is Objetivo.COMPLETAR:
		return _ejercicio_completar(id_ejercicio, forma, aleatorio, nivel or Nivel.FACIL)
	nivel = _NIVEL.get(objetivo, Nivel.FACIL)
	for _intento in range(_SUDOKUS):
		enunciado, solucion = generador.generar(nivel, aleatorio, forma)
		momentos = _momentos(enunciado)
		if objetivo is Objetivo.NOTAS:
			ejercicio = _ejercicio_notas(id_ejercicio, momentos, solucion, forma, aleatorio)
			if ejercicio is not None:
				return ejercicio
			continue
		if objetivo in (Objetivo.UNICO_LUGAR_LINEA, Objetivo.UNICO_NUMERO):
			validos = [_Momento(m.valores, p) for m in momentos for p in _colocaciones(m.valores, objetivo)]
		else:
			validos = [m for m in momentos if _cumple(objetivo, m.paso)]
		aleatorio.shuffle(validos)
		for momento in validos:
			if not momento.paso.eliminaciones:
				return _ejercicio_tecnica(id_ejercicio, momento, solucion, forma)
			ejercicio = _ejercicio_descarte(id_ejercicio, momento, solucion, forma)
			if ejercicio is not None:
				return ejercicio
	raise RuntimeError(f"No se encontró un ejercicio de {objetivo}")


def _ejercicio_completar(
	id_ejercicio: str,
	forma: Forma,
	aleatorio: random.Random,
	nivel: Nivel,
) -> Ejercicio:
	enunciado, solucion = generador.generar(nivel, aleatorio, forma)
	return Ejercicio(
		id=id_ejercicio,
		tipo=TipoEjercicio.COMPLETAR,
		tablero=tuple(enunciado),
		escritos=tuple([0] * forma.casillas),
		solucion=tuple(solucion),
		objetivos=(),
		inicio=0,
		# Translators: instruction of an exercise where the whole sudoku is solved.
		instruccion=_("Solve the whole sudoku. Press P or Shift+P whenever you need a hint."),
		# Sin pistas escritas: las da el resolutor desde el tablero de cada momento.
		pistas=(),
	)


def _ejercicio_tecnica(id_ejercicio: str, momento: _Momento, solucion: list[int], forma: Forma) -> Ejercicio:
	paso = momento.paso
	lado = forma.lado
	orientacion = anunciador.orientar_paso(paso, lado)
	# Translators: after the instruction of an exercise about a technique.
	tarea = _("Find it and write it.")
	instruccion = f"{orientacion} {tarea}"
	# El cursor empieza en la primera casilla del grupo que se mira (o de la fila de la casilla).
	if paso.grupo is not None:
		inicio = forma.indices_de(paso.grupo)[0]
	else:
		inicio = (paso.indice // lado) * lado
	return Ejercicio(
		id=id_ejercicio,
		tipo=TipoEjercicio.ESCRIBIR,
		tablero=tuple(momento.valores),
		escritos=tuple([0] * forma.casillas),
		solucion=tuple(solucion),
		objetivos=(paso.indice,),
		inicio=inicio,
		instruccion=instruccion,
		pistas=(_pista_breve(paso, lado), anunciador.explicar_paso(paso, lado)),
		orientacion=orientacion,
	)


def _texto_quitar(quitar: list[tuple[int, int]], lado: int) -> str:
	"""«Quita la nota 7 de la fila 3, columna 7.», una frase por casilla."""
	por_casilla: dict[int, list[int]] = {}
	for indice, numero in quitar:
		por_casilla.setdefault(indice, []).append(numero)
	frases = []
	for indice, numeros in por_casilla.items():
		frases.append(
			ngettext(
				# Translators: what to do in the first step of an intersection or pair exercise, as in "Remove note 7 from the row 3, column 7."
				"Remove note {numbers} from {cell}.",
				"Remove notes {numbers} from {cell}.",
				len(numeros),
			).format(numbers=anunciador.unir(sorted(numeros)), cell=anunciador.posicion(indice, lado)),
		)
	return " ".join(frases)


def _ejercicio_descarte(
	id_ejercicio: str,
	momento: _Momento,
	solucion: list[int],
	forma: Forma,
) -> Ejercicio | None:
	"""Intersección o pareja en dos pasos sobre el mismo tablero, con las notas ya puestas.

	Paso 1: quitar las notas que se descartan y que importan para llegar al número
	(las de la casilla, o las de ese número en el grupo donde va). Paso 2: escribir el número.
	Así cada paso nombra un solo lugar.
	"""
	paso = momento.paso
	lado = forma.lado
	(eliminacion,) = paso.eliminaciones
	if paso.grupo is None:
		quitar = [(i, n) for i, n in eliminacion.quitados if i == paso.indice]
	else:
		del_grupo = set(forma.indices_de(paso.grupo))
		quitar = [(i, n) for i, n in eliminacion.quitados if i in del_grupo and n == paso.numero]
	if not quitar:
		return None
	# Notas en todas las casillas vacías de los grupos que intervienen, como las pondría una persona.
	grupos = {eliminacion.grupo}
	if eliminacion.otro is not None:
		grupos.add(eliminacion.otro)
	grupos.update([paso.grupo] if paso.grupo is not None else forma.grupos_de(paso.indice))
	candidatos = tecnicas.Resolutor(momento.valores).candidatos
	casillas = sorted({i for g in grupos for i in forma.indices_de(g) if not momento.valores[i]})
	notas = tuple((i, tuple(sorted(candidatos[i]))) for i in casillas)
	accion = _texto_quitar(quitar, lado)
	celda = anunciador.posicion(paso.indice, lado)
	# Translators: before the first step of an intersection or pair exercise.
	paso_1 = _("Step 1 of 2.")
	# Translators: before the second step of an intersection or pair exercise.
	paso_2 = _("Step 2 of 2.")
	if paso.grupo is None:
		# Translators: second step of an exercise, as in "Now only one note is left in the row 3, column 7. Write that number."
		tarea = _("Now only one note is left in {cell}. Write that number.").format(cell=celda)
		# Translators: said when writing in another cell in the second step, as in "Not here. Write in the row 3, column 7."
		orientacion = _("Write in {cell}.").format(cell=celda)
		# Translators: short hint of the second step, as in "Press N in the row 3, column 7: only one note is left."
		breve = _("Press N in {cell}: only one note is left.").format(cell=celda)
	else:
		grupo = anunciador.grupo_en_frase(paso.grupo)
		tarea = _(
			# Translators: second step of an exercise, as in "Now, in the row 2, the 1 only fits in one cell. Find it and write it."
			"Now, in {group}, the {number} only fits in one cell. Find it and write it.",
		).format(group=grupo, number=paso.numero)
		# Translators: said when writing in another cell in the second step, as in "In the row 2, the 1 only fits in one cell now."
		orientacion = _("In {group}, the {number} only fits in one cell now.").format(
			group=grupo,
			number=paso.numero,
		)
		breve = _(
			# Translators: short hint of the second step, as in "Press N in the empty cells of the row 2: only one still has note 1."
			"Press N in the empty cells of {group}: only one still has note {number}.",
		).format(group=grupo, number=paso.numero)
	segundo = Ejercicio(
		id=id_ejercicio,
		tipo=TipoEjercicio.ESCRIBIR,
		tablero=tuple(momento.valores),
		escritos=tuple([0] * forma.casillas),
		solucion=tuple(solucion),
		objetivos=(paso.indice,),
		inicio=quitar[0][0],
		instruccion=f"{paso_2} {tarea}",
		# Translators: full hint of the second step, as in "The 8 goes in the row 3, column 7."
		pistas=(breve, _("The {number} goes in {cell}.").format(number=paso.numero, cell=celda)),
		orientacion=orientacion,
	)
	return Ejercicio(
		id=id_ejercicio,
		tipo=TipoEjercicio.QUITAR_NOTAS,
		tablero=tuple(momento.valores),
		escritos=tuple([0] * forma.casillas),
		solucion=tuple(solucion),
		objetivos=tuple(sorted({i for i, _n in quitar})),
		inicio=quitar[0][0],
		instruccion=f"{paso_1} {anunciador.explicar_eliminacion(eliminacion, lado)} {accion}",
		pistas=(
			_(
				# Translators: short hint of the first step of an intersection or pair exercise.
				"Notes are removed with Shift and the number, the same keys that add them. N reads the notes of a cell.",
			),
			accion,
		),
		orientacion=accion,
		notas=notas,
		quitar=tuple(quitar),
		segundo=segundo,
	)


def _pista_breve(paso: Paso, lado: int) -> str:
	if paso.tecnica is Tecnica.ULTIMO_NUMERO and paso.grupo is not None:
		tecla = {TipoGrupo.FILA: "F", TipoGrupo.COLUMNA: "C", TipoGrupo.BLOQUE: "B"}[paso.grupo.tipo]
		# Translators: short hint of an exercise, as in "Press B inside the block 4 to hear which number is missing."
		return _("Press {key} inside {group} to hear which number is missing.").format(
			key=tecla,
			group=anunciador.grupo_en_frase(paso.grupo),
		)
	if paso.tecnica is Tecnica.UNICO_LUGAR and paso.grupo is not None:
		# Translators: short hint of an exercise, as in "Look for the 7: in the block 4 it only fits in one cell."
		return _("Look for the {number}: in {group} it only fits in one cell.").format(
			number=paso.numero,
			group=anunciador.grupo_en_frase(paso.grupo),
		)
	return _(
		# Translators: short hint of an exercise about a cell where only one number fits.
		"Go through the empty cells of the row {row} and press C and B in each one: "
		"in one of them only one number fits.",
	).format(row=paso.indice // lado + 1)


def _ejercicio_notas(
	id_ejercicio: str,
	momentos: list[_Momento],
	solucion: list[int],
	forma: Forma,
	aleatorio: random.Random,
) -> Ejercicio | None:
	"""Una casilla vacía con 2 o 3 números posibles, a mitad del sudoku."""
	if len(momentos) < 4:
		return None
	momento = momentos[aleatorio.randrange(len(momentos) // 4, len(momentos) * 3 // 4)]
	resolutor = tecnicas.Resolutor(momento.valores)
	opciones = [i for i in range(forma.casillas) if 2 <= len(resolutor.candidatos[i]) <= 3]
	if not opciones:
		return None
	indice = aleatorio.choice(opciones)
	celda = anunciador.posicion(indice, forma.lado)
	candidatos = sorted(resolutor.candidatos[indice])
	return Ejercicio(
		id=id_ejercicio,
		tipo=TipoEjercicio.NOTAS,
		tablero=tuple(momento.valores),
		escritos=tuple([0] * forma.casillas),
		solucion=tuple(solucion),
		objetivos=(indice,),
		inicio=indice,
		# Translators: instruction of an exercise about notes, as in "Write as notes in the row 3, column 5 all the numbers that can go there."
		instruccion=_("Write as notes in {cell} all the numbers that can go there.").format(cell=celda),
		pistas=(
			# Translators: short hint of an exercise about notes.
			_("Press F, C and B to hear which numbers are already in its row, its column and its block."),
			# Translators: full hint of an exercise about notes, as in "The numbers that can go are 3, 5 and 8."
			_("The numbers that can go are {numbers}.").format(numbers=anunciador.unir(candidatos)),
		),
	)
