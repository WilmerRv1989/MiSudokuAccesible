# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Ventana del tablero: el dibujo para quien ve la pantalla, el menú del tablero y el guardado."""

import time
from collections.abc import Callable

import addonHandler
import ui
import winUser
import wx
from gui.message import MessageDialog, ReturnCode
from logHandler import log

from ..nucleo.tablero_virtual import CuadriculaVirtual
from ..sudoku import anunciador
from ..sudoku.tablero import Sudoku
from . import archivos, atajos, sonidos
from .tablero_sudoku import CuadriculaSudoku

addonHandler.initTranslation()

# Colores del dibujo: contraste alto entre casillas, números, líneas y foco.
_COLOR_FONDO = wx.Colour(40, 40, 40)
_COLOR_CASILLA = wx.Colour(255, 255, 255)
_COLOR_LINEA = wx.Colour(150, 150, 150)
_COLOR_LINEA_BLOQUE = wx.Colour(0, 0, 0)
_COLOR_FOCO = wx.Colour(30, 111, 217)
_COLOR_FIJO = wx.Colour(0, 0, 0)
_COLOR_ESCRITO = wx.Colour(20, 70, 170)
_COLOR_NOTA = wx.Colour(90, 90, 90)

_MARGEN = 20
_TAMANO_INICIAL = 600


class PanelTablero(wx.Panel):
	"""Dibuja el tablero y recibe el foco del sistema. NVDA lo cambia por la casilla virtual."""

	def __init__(self, padre: wx.Window, nombre: str) -> None:
		super().__init__(padre, style=wx.WANTS_CHARS)
		self.SetLabel(nombre)
		self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
		self.cuadricula: CuadriculaVirtual | None = None
		self.Bind(wx.EVT_PAINT, self._al_pintar)
		self.Bind(wx.EVT_SIZE, lambda evento: self.Refresh())

	def AcceptsFocus(self) -> bool:
		return True

	def _lado_casilla(self) -> int:
		ancho, alto = self.GetClientSize()
		casillas = self.cuadricula.filas if self.cuadricula is not None else 1
		return max(8, (min(ancho, alto) - 2 * _MARGEN) // casillas)

	def rectangulo_casilla(self, fila: int, columna: int) -> tuple[int, int, int, int]:
		lado = self._lado_casilla()
		return (_MARGEN + columna * lado, _MARGEN + fila * lado, lado, lado)

	def _al_pintar(self, evento: wx.PaintEvent) -> None:
		dc = wx.AutoBufferedPaintDC(self)
		dc.SetBackground(wx.Brush(_COLOR_FONDO))
		dc.Clear()
		cuadricula = self.cuadricula
		if cuadricula is None:
			return
		lado = self._lado_casilla()
		casillas = cuadricula.filas
		total = lado * casillas
		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.SetBrush(wx.Brush(_COLOR_CASILLA))
		dc.DrawRectangle(_MARGEN, _MARGEN, total, total)
		self._pintar_contenido(dc, lado)
		# Líneas finas entre casillas y gruesas entre bloques.
		alto_bloque, ancho_bloque = self._medidas_bloque()
		fina = wx.Pen(_COLOR_LINEA, 1)
		gruesa = wx.Pen(_COLOR_LINEA_BLOQUE, max(2, lado // 12))
		for indice in range(casillas + 1):
			posicion = _MARGEN + indice * lado
			dc.SetPen(gruesa if indice % alto_bloque == 0 else fina)
			dc.DrawLine(_MARGEN, posicion, _MARGEN + total, posicion)
			dc.SetPen(gruesa if indice % ancho_bloque == 0 else fina)
			dc.DrawLine(posicion, _MARGEN, posicion, _MARGEN + total)
		x, y, _ancho, _alto = self.rectangulo_casilla(cuadricula.fila, cuadricula.columna)
		dc.SetBrush(wx.TRANSPARENT_BRUSH)
		dc.SetPen(wx.Pen(_COLOR_FOCO, max(3, lado // 10)))
		dc.DrawRectangle(x, y, lado, lado)

	def _medidas_bloque(self) -> tuple[int, int]:
		"""Filas y columnas de cada bloque (3 por 3 en el tablero de 9)."""
		if isinstance(self.cuadricula, CuadriculaSudoku):
			forma = self.cuadricula.sudoku.forma
			return forma.alto_bloque, forma.ancho_bloque
		return 3, 3

	def _pintar_contenido(self, dc: wx.DC, lado: int) -> None:
		"""Los números (los fijos en negrita) y las notas, en una cuadrícula pequeña de 3 por 3."""
		cuadricula = self.cuadricula
		if not isinstance(cuadricula, CuadriculaSudoku):
			return
		sudoku = cuadricula.sudoku
		fuente_fija = wx.Font(wx.FontInfo(max(6, int(lado * 0.45))).Bold())
		fuente_escrita = wx.Font(wx.FontInfo(max(6, int(lado * 0.45))))
		fuente_nota = wx.Font(wx.FontInfo(max(5, int(lado * 0.16))))
		tercio = lado / 3
		for indice in range(sudoku.forma.casillas):
			fila, columna = divmod(indice, sudoku.forma.lado)
			x, y, _ancho, _alto = self.rectangulo_casilla(fila, columna)
			valor = sudoku.valores[indice]
			if valor:
				fija = sudoku.es_fija(indice)
				dc.SetFont(fuente_fija if fija else fuente_escrita)
				dc.SetTextForeground(_COLOR_FIJO if fija else _COLOR_ESCRITO)
				texto = str(valor)
				ancho_texto, alto_texto = dc.GetTextExtent(texto)
				dc.DrawText(texto, x + (lado - ancho_texto) // 2, y + (lado - alto_texto) // 2)
				continue
			dc.SetFont(fuente_nota)
			dc.SetTextForeground(_COLOR_NOTA)
			for nota in sudoku.notas[indice]:
				sub_fila, sub_columna = divmod(nota - 1, 3)
				texto = str(nota)
				ancho_texto, alto_texto = dc.GetTextExtent(texto)
				dc.DrawText(
					texto,
					int(x + sub_columna * tercio + (tercio - ancho_texto) / 2),
					int(y + sub_fila * tercio + (tercio - alto_texto) / 2),
				)


class VentanaBase(wx.Frame):
	"""Ventana con un tablero: lo que compartirán el juego y las lecciones."""

	cuadricula: CuadriculaVirtual

	def __init__(self, titulo: str, nombre_tablero: str, al_cerrar: Callable[[], None]) -> None:
		super().__init__(None, title=titulo, size=(_TAMANO_INICIAL, _TAMANO_INICIAL))
		self._al_cerrar = al_cerrar
		self._cerrando_sin_preguntar = False
		self._iniciada = False
		self.panel = PanelTablero(self, nombre_tablero)
		self.Bind(wx.EVT_CLOSE, self._al_cerrar_ventana)
		self.Bind(wx.EVT_ACTIVATE, self._al_activar)
		self.CentreOnScreen()

	def _instalar(self, cuadricula: CuadriculaVirtual) -> None:
		"""Cada subclase crea su cuadrícula después de inicializar la ventana y la instala aquí."""
		self.cuadricula = cuadricula
		self.panel.cuadricula = cuadricula

	def _al_mostrar_por_primera_vez(self) -> None:
		"""Se llama una sola vez, cuando la ventana se muestra por primera vez."""

	def _confirmar_cierre(self) -> bool:
		"""Si devuelve False, la ventana no se cierra."""
		return True

	def mostrar(self) -> None:
		self.Show()
		self.Raise()
		winUser.setForegroundWindow(self.GetHandle())
		self.panel.SetFocus()
		if not self._iniciada:
			self._iniciada = True
			self._al_mostrar_por_primera_vez()

	def cerrar_sin_preguntar(self) -> None:
		self._cerrando_sin_preguntar = True
		self.Close(force=True)

	def _al_activar(self, evento: wx.ActivateEvent) -> None:
		if evento.GetActive():
			self.panel.SetFocus()
		evento.Skip()

	def _al_cerrar_ventana(self, evento: wx.CloseEvent) -> None:
		if not self._cerrando_sin_preguntar and evento.CanVeto() and not self._confirmar_cierre():
			evento.Veto()
			return
		self._antes_de_destruir()
		self.cuadricula.cerrar()
		self._al_cerrar()
		self.Destroy()

	def _antes_de_destruir(self) -> None:
		"""Se llama justo antes de cerrar la ventana."""

	def _confirmar(self, mensaje: str, titulo: str) -> bool:
		"""Pregunta Aceptar o Cancelar."""
		return MessageDialog.confirm(mensaje, titulo, parent=self) == ReturnCode.OK

	def mostrar_menu(self, opciones: list[tuple[str, Callable[[], None], bool]]) -> None:
		"""Menú emergente sobre la casilla actual. Cada opción: (texto, acción, habilitada)."""
		menu = wx.Menu()
		for texto, accion, habilitada in opciones:
			elemento = menu.Append(wx.ID_ANY, texto)
			elemento.Enable(habilitada)
			menu.Bind(wx.EVT_MENU, lambda evento, accion=accion: wx.CallAfter(accion), elemento)
		wx.CallAfter(self._abrir_menu, menu)

	def _abrir_menu(self, menu: wx.Menu) -> None:
		x, y, lado, _alto = self.panel.rectangulo_casilla(self.cuadricula.fila, self.cuadricula.columna)
		try:
			self.panel.PopupMenu(menu, wx.Point(x + lado // 2, y + lado // 2))
		finally:
			menu.Destroy()


class VentanaSudoku(VentanaBase):
	"""Ventana del sudoku. Se cierra con Escape, con Alt+F4 o desde su menú, sin perder nada:
	cada cambio se guarda, y el tiempo cuenta solo mientras la ventana está activa."""

	cuadricula: CuadriculaSudoku

	def __init__(
		self,
		sudoku: Sudoku,
		al_cerrar: Callable[[], None],
		al_pedir_nuevo: Callable[[], None],
		al_resolver: Callable[[Sudoku], str],
	) -> None:
		if sudoku.del_dia:
			# Translators: title of the window of the sudoku of the day, as in "MiSudokuAccesible - Sudoku of the day, Medium".
			titulo = _("MiSudokuAccesible - Sudoku of the day, {level}").format(
				level=anunciador.etiqueta_nivel(sudoku.nivel),
			)
		else:
			# Translators: title of the sudoku board window, as in "MiSudokuAccesible - 9 by 9, Easy".
			titulo = _("MiSudokuAccesible - {size}, {level}").format(
				size=anunciador.etiqueta_tamano(sudoku.forma.lado),
				level=anunciador.etiqueta_nivel(sudoku.nivel),
			)
		if not sudoku.ayudas:
			# Translators: added to the title of the board window of a sudoku without help.
			sin_ayudas = _("without help")
			titulo = f"{titulo}, {sin_ayudas}"
		super().__init__(
			titulo,
			# Translators: accessible name of the sudoku board.
			_("Sudoku board"),
			al_cerrar,
		)
		self.sudoku = sudoku
		self._al_pedir_nuevo = al_pedir_nuevo
		self._al_resolver = al_resolver
		# Momento en que la ventana se activó por última vez (None si no está activa).
		self._activa_desde: float | None = None
		self._instalar(CuadriculaSudoku(self.panel, self))

	# Tiempo.

	def _al_activar(self, evento: wx.ActivateEvent) -> None:
		if evento.GetActive():
			# Al volver a la ventana se dice también el bloque de la casilla.
			self.cuadricula.olvidar_bloque()
			if not self.sudoku.resuelto:
				self._activa_desde = time.monotonic()
		else:
			self._sumar_tiempo()
			self._activa_desde = None
		super()._al_activar(evento)

	def _sumar_tiempo(self) -> None:
		if self._activa_desde is None:
			return
		ahora = time.monotonic()
		self.sudoku.segundos += ahora - self._activa_desde
		self._activa_desde = ahora

	# Guardado.

	def guardar_automatico(self) -> None:
		"""Guarda el sudoku para continuarlo. Uno resuelto se borra: ya no hay nada que continuar."""
		self._sumar_tiempo()
		# El sudoku del día tiene su propio archivo: no pisa el sudoku normal que esté a medias.
		ruta = (
			archivos.ruta_guardado_del_dia() if self.sudoku.del_dia else archivos.ruta_guardado_automatico()
		)
		if self.sudoku.resuelto:
			archivos.borrar(ruta)
			return
		try:
			archivos.escribir(ruta, self.sudoku.a_json())
		except OSError:
			log.error("No se pudo guardar el sudoku en curso", exc_info=True)

	def al_cambiar(self) -> None:
		"""Se llama después de cada cambio en el tablero."""
		self.guardar_automatico()

	def al_resolver(self) -> None:
		self._sumar_tiempo()
		self._activa_desde = None
		self.guardar_automatico()
		sonidos.reproducir(sonidos.RESUELTO)
		# Quien abrió la ventana anota las estadísticas y puede añadir algo: los días seguidos o un récord.
		extra = self._al_resolver(self.sudoku)
		ui.message(f"{anunciador.describir_resuelto(self.sudoku.segundos)} {extra}".strip())

	def _antes_de_destruir(self) -> None:
		self.guardar_automatico()

	# Menú del tablero.

	def mostrar_menu_tablero(self) -> None:
		self.mostrar_menu(
			[
				# Translators: item of the menu of the sudoku board.
				(_("&New sudoku..."), self._al_pedir_nuevo, True),
				# Translators: item of the menu of the sudoku board.
				(_("C&heck"), self._comprobar, not self.sudoku.resuelto),
				# Translators: item of the menu of the sudoku board.
				(_("&Restart"), self._reiniciar, self.sudoku.empezado),
				# Translators: item of the menu of the board and of the lessons.
				(_("&Keyboard shortcuts"), self.mostrar_atajos, True),
				# Translators: item of the menu of the sudoku board.
				(_("&Close the board"), self.Close, True),
			],
		)

	def mostrar_atajos(self) -> None:
		wx.CallAfter(atajos.mostrar, {atajos.Contexto.JUEGO: self.cuadricula.celda_actual})

	def _comprobar(self) -> None:
		# Al cerrar el menú, NVDA anuncia la casilla: el resultado se dice después.
		self.cuadricula.decir_al_volver(
			anunciador.describir_comprobacion(self.sudoku.errores(), self.sudoku.vacias()),
		)

	def _reiniciar(self) -> None:
		if not self._confirmar(
			_(
				# Translators: asked before restarting the sudoku.
				"All the numbers and notes you wrote will be deleted, and the time goes back to zero. Restart?",
			),
			# Translators: title of the confirmation to restart the sudoku.
			_("Restart"),
		):
			return
		self.sudoku.reiniciar()
		if self.IsActive():
			self._activa_desde = time.monotonic()
		self.panel.Refresh()
		self.guardar_automatico()
		# Translators: said after restarting the sudoku, followed by how many empty cells are left.
		reiniciado = _("Sudoku restarted.")
		self.cuadricula.decir_al_volver(f"{reiniciado} {anunciador.describir_vacias(self.sudoku.vacias())}")
