# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""El sudoku del día: uno por fecha, el mismo para todas las personas con la misma versión.

Sale de la fecha: se usa como semilla del generador. El nivel depende del día de la semana.
"""

import datetime
import random

from . import generador
from .generador import Nivel
from .grupos import NUEVE
from .tablero import Sudoku

# Lunes y martes, fácil; miércoles y jueves, medio; viernes, difícil; sábado y domingo, fácil.
_NIVEL_POR_DIA = [
	Nivel.FACIL,
	Nivel.FACIL,
	Nivel.MEDIO,
	Nivel.MEDIO,
	Nivel.DIFICIL,
	Nivel.FACIL,
	Nivel.FACIL,
]


def nivel_del_dia(fecha: datetime.date) -> Nivel:
	return _NIVEL_POR_DIA[fecha.weekday()]


def sudoku_del_dia(fecha: datetime.date, ayudas: bool = True) -> Sudoku:
	nivel = nivel_del_dia(fecha)
	aleatorio = random.Random(int(fecha.strftime("%Y%m%d")))
	enunciado, solucion = generador.generar(nivel, aleatorio, NUEVE)
	sudoku = Sudoku(enunciado, solucion, nivel)
	sudoku.del_dia = fecha.isoformat()
	sudoku.ayudas = ayudas
	return sudoku
