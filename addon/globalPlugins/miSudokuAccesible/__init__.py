# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Punto de entrada del complemento: el submenú en Herramientas de NVDA y el tablero abierto."""

import datetime
import os
import threading
from collections.abc import Callable

import addonHandler
import globalPluginHandler
import globalVars
import gui
import ui
import wx
from gui.message import MessageDialog, ReturnCode, displayDialogAsModal
from logHandler import log
from NVDAObjects import NVDAObject
from NVDAObjects.window import Window
from scriptHandler import script

from .interfaz import archivos, atajos, estadisticas, preferencias
from .interfaz.curso import ControladorCurso
from .interfaz.panel_configuracion import PanelMiSudoku
from .interfaz.tablero_leccion import CeldaLeccion
from .interfaz.tablero_sudoku import CeldaSudoku
from .interfaz.dialogos import DialogoNuevoSudoku
from .interfaz.ventana_tablero import VentanaSudoku
from .nucleo import tablero_virtual
from .sudoku import diario, generador, idioma
from .sudoku.estadisticas import Estadisticas, texto_racha
from .sudoku.grupos import Forma
from .sudoku.tablero import Sudoku

addonHandler.initTranslation()
idioma.configurar(_, ngettext)

# Translators: name of the add-on, used as the submenu label and the input gestures category.
NOMBRE = _("MiSudokuAccesible")

# Lo último elegido en el diálogo de nuevo sudoku.
preferencias.registrar()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = NOMBRE

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._elemento_submenu: wx.MenuItem | None = None
		self._elemento_continuar: wx.MenuItem | None = None
		self._ventana: VentanaSudoku | None = None
		self._curso: ControladorCurso | None = None
		# Mientras se genera un sudoku en otro hilo, no se empieza otro.
		self._generando = False
		self._terminado = False
		# En las pantallas seguras (inicio de sesión, control de cuentas) no hay menús ni ventanas.
		if globalVars.appArgs.secure:
			return
		self._crear_menu()
		self._actualizar_menu()
		PanelMiSudoku.al_borrar_progreso = self._borrar_progreso
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(PanelMiSudoku)

	# Menú en Herramientas.

	def _crear_menu(self) -> None:
		bandeja = gui.mainFrame.sysTrayIcon
		self._submenu = wx.Menu()
		nuevo = self._submenu.Append(
			wx.ID_ANY,
			# Translators: item of the add-on submenu that starts a new sudoku.
			_("&New sudoku..."),
			# Translators: help text of the "New sudoku" menu item.
			_("Choose a level and start a new sudoku"),
		)
		bandeja.Bind(wx.EVT_MENU, lambda evento: self.nuevo_sudoku(), nuevo)
		del_dia = self._submenu.Append(
			wx.ID_ANY,
			# Translators: item of the add-on submenu that opens the sudoku of the day.
			_("Sudoku of the &day"),
			# Translators: help text of the "Sudoku of the day" menu item.
			_("A new sudoku every day, the same for everyone"),
		)
		bandeja.Bind(wx.EVT_MENU, lambda evento: self.sudoku_del_dia(), del_dia)
		aprender = self._submenu.Append(
			wx.ID_ANY,
			# Translators: item of the add-on submenu that opens the sudoku course.
			_("&Learn to play..."),
			# Translators: help text of the "Learn to play" menu item.
			_("Guided lessons to learn sudoku step by step"),
		)
		bandeja.Bind(wx.EVT_MENU, lambda evento: self.aprender_a_jugar(), aprender)
		elemento_estadisticas = self._submenu.Append(
			wx.ID_ANY,
			# Translators: item of the add-on submenu that shows the statistics.
			_("My &statistics..."),
			# Translators: help text of the "My statistics" menu item.
			_("Sudokus solved, best times, days in a row and your progress in the course"),
		)
		bandeja.Bind(wx.EVT_MENU, lambda evento: wx.CallAfter(estadisticas.mostrar), elemento_estadisticas)
		elemento_atajos = self._submenu.Append(
			wx.ID_ANY,
			# Translators: item of the add-on submenu that shows all the keyboard shortcuts.
			_("&Keyboard shortcuts..."),
			# Translators: help text of the "Keyboard shortcuts" menu item.
			_("The keys of the board and of the lessons"),
		)
		bandeja.Bind(wx.EVT_MENU, lambda evento: self.mostrar_atajos(), elemento_atajos)
		self._elemento_continuar = wx.MenuItem(
			self._submenu,
			wx.ID_ANY,
			# Translators: item of the add-on submenu that opens the sudoku in progress.
			_("&Continue the sudoku"),
			# Translators: help text of the "Continue the sudoku" menu item.
			_("Open the sudoku you left unfinished"),
		)
		bandeja.Bind(wx.EVT_MENU, lambda evento: self.continuar_sudoku(), self._elemento_continuar)
		self._elemento_submenu = bandeja.toolsMenu.AppendSubMenu(
			self._submenu,
			# Translators: label of the add-on submenu inside NVDA's Tools menu.
			_("Mi&SudokuAccesible"),
			# Translators: help text of the add-on submenu.
			_("Accessible sudoku"),
		)

	def _ventana_normal(self) -> VentanaSudoku | None:
		"""La ventana abierta si es de un sudoku normal (no del sudoku del día)."""
		if self._ventana is not None and not self._ventana.sudoku.del_dia:
			return self._ventana
		return None

	def _hay_para_continuar(self) -> bool:
		"""Si hay un sudoku normal sin terminar: abierto o guardado."""
		ventana = self._ventana_normal()
		if ventana is not None:
			return not ventana.sudoku.resuelto
		return os.path.isfile(archivos.ruta_guardado_automatico())

	def _actualizar_menu(self) -> None:
		"""«Continuar el sudoku» solo aparece si hay uno sin terminar."""
		elemento = self._elemento_continuar
		if elemento is None:
			return
		hay = self._hay_para_continuar()
		esta_en_menu = self._submenu.FindItemById(elemento.GetId()) is not None
		if hay and not esta_en_menu:
			# Justo después de «Nuevo sudoku...».
			self._submenu.Insert(1, elemento)
		elif not hay and esta_en_menu:
			self._submenu.Remove(elemento)

	def terminate(self) -> None:
		self._terminado = True
		if PanelMiSudoku in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(PanelMiSudoku)
		PanelMiSudoku.al_borrar_progreso = None
		preferencias.quitar()
		if self._curso is not None:
			self._curso.cerrar()
			self._curso = None
		if self._ventana is not None:
			# Se guarda al cerrarse, para continuarlo al volver a NVDA.
			self._ventana.cerrar_sin_preguntar()
			self._ventana = None
		if (
			self._elemento_continuar is not None
			and self._submenu.FindItemById(self._elemento_continuar.GetId()) is None
		):
			# Si no está en el menú, nadie más lo destruye.
			self._elemento_continuar.Destroy()
		self._elemento_continuar = None
		if self._elemento_submenu is not None:
			try:
				gui.mainFrame.sysTrayIcon.toolsMenu.Remove(self._elemento_submenu)
				self._elemento_submenu.Destroy()
			except (RuntimeError, AttributeError):
				log.debugWarning("No se pudo quitar el menú de MiSudokuAccesible", exc_info=True)
			self._elemento_submenu = None
		super().terminate()

	# Curso «Aprender a jugar».

	def aprender_a_jugar(self) -> None:
		if self._curso is None:
			try:
				self._curso = ControladorCurso()
			except Exception:
				log.error("No se pudo cargar el curso de MiSudokuAccesible", exc_info=True)
				return
		self._curso.abrir_lista()

	@script(
		# Translators: description of the command that opens the sudoku course, shown in the Input gestures dialog.
		description=_("Opens the sudoku course Learn to play"),
	)
	def script_aprender_a_jugar(self, gesture) -> None:
		self.aprender_a_jugar()

	# Sudoku guardado.

	def _leer_guardado(self, ruta: str | None = None) -> Sudoku | None:
		"""El sudoku sin terminar que quedó guardado. Si el archivo está dañado, se borra."""
		ruta = ruta or archivos.ruta_guardado_automatico()
		if not os.path.isfile(ruta):
			return None
		try:
			return Sudoku.desde_json(archivos.leer(ruta))
		except (OSError, ValueError):
			log.debugWarning("No se pudo leer el sudoku guardado", exc_info=True)
			archivos.borrar(ruta)
			return None

	def _hay_sudoku_a_medias(self) -> bool:
		"""Si hay un sudoku sin terminar con algo escrito, que se perdería al empezar otro."""
		ventana = self._ventana_normal()
		if ventana is not None:
			sudoku: Sudoku | None = ventana.sudoku
		else:
			sudoku = self._leer_guardado()
		return sudoku is not None and sudoku.empezado and not sudoku.resuelto

	# Tablero.

	def nuevo_sudoku(self) -> None:
		wx.CallAfter(self._nuevo_sudoku)

	def _nuevo_sudoku(self) -> None:
		if self._generando:
			# Translators: reported when asking for a new sudoku while another one is being prepared.
			ui.message(_("A sudoku is already being prepared."))
			return
		padre = self._ventana if self._ventana is not None and self._ventana.IsShown() else None
		dialogo = DialogoNuevoSudoku(
			padre,
			preferencias.forma_guardada(),
			preferencias.nivel_guardado(),
			preferencias.ayudas_guardadas(),
		)
		try:
			if displayDialogAsModal(dialogo) != wx.ID_OK:
				return
			forma = dialogo.forma_elegida()
			nivel = dialogo.nivel_elegido()
			ayudas = dialogo.ayudas_elegidas()
		finally:
			dialogo.Destroy()
		preferencias.guardar(forma, nivel, ayudas)
		if self._hay_sudoku_a_medias():
			respuesta = MessageDialog.confirm(
				_(
					# Translators: asked when starting a new sudoku while another one is unfinished.
					"You have an unfinished sudoku. If you start a new one, it will be lost. Start a new sudoku?",
				),
				# Translators: title of the confirmation to start a new sudoku.
				_("New sudoku"),
				parent=padre,
			)
			if respuesta != ReturnCode.OK:
				return
		# Translators: said while a new sudoku is generated (it can take a couple of seconds).
		self._generar(_("Preparing the sudoku..."), lambda: self._sudoku_nuevo(forma, nivel, ayudas))

	@staticmethod
	def _sudoku_nuevo(forma: Forma, nivel: generador.Nivel, ayudas: bool) -> Sudoku:
		enunciado, solucion = generador.generar(nivel, forma=forma)
		sudoku = Sudoku(enunciado, solucion, nivel)
		sudoku.ayudas = ayudas
		return sudoku

	def _generar(self, aviso: str, crear: Callable[[], Sudoku]) -> None:
		"""En otro hilo: un sudoku medio o difícil puede tardar un par de segundos, y NVDA no debe pararse."""
		self._generando = True
		ui.message(aviso)

		def generar() -> None:
			try:
				sudoku: Sudoku | None = crear()
			except Exception:
				log.error("No se pudo generar el sudoku", exc_info=True)
				sudoku = None
			wx.CallAfter(self._al_generar, sudoku)

		threading.Thread(target=generar, daemon=True).start()

	def _al_generar(self, sudoku: Sudoku | None) -> None:
		self._generando = False
		if self._terminado:
			return
		if sudoku is None:
			# Translators: reported when a new sudoku could not be generated.
			ui.message(_("The sudoku could not be prepared. Please try again."))
			return
		self._abrir(sudoku)

	def continuar_sudoku(self) -> None:
		wx.CallAfter(self._continuar_sudoku)

	def _continuar_sudoku(self) -> None:
		ventana = self._ventana_normal()
		if ventana is not None:
			ventana.mostrar()
			return
		sudoku = self._leer_guardado()
		if sudoku is None:
			self._actualizar_menu()
			MessageDialog.alert(
				# Translators: reported when the saved sudoku cannot be opened.
				_("The unfinished sudoku could not be opened. You can start a new one."),
				# Translators: title of the message about the saved sudoku.
				_("Continue the sudoku"),
			)
			return
		self._abrir(sudoku)

	def _abrir(self, sudoku: Sudoku) -> None:
		"""Abre un sudoku. La ventana que hubiera se cierra: su sudoku queda guardado."""
		if self._ventana is not None:
			self._ventana.cerrar_sin_preguntar()
			self._ventana = None
		self._ventana = VentanaSudoku(
			sudoku,
			al_cerrar=self._al_cerrar_ventana,
			al_pedir_nuevo=self.nuevo_sudoku,
			al_resolver=self._al_resolver,
		)
		# Un sudoku nuevo sustituye al que quedó guardado.
		self._ventana.guardar_automatico()
		self._ventana.mostrar()
		self._actualizar_menu()

	def _al_resolver(self, sudoku: Sudoku) -> str:
		"""Anota el sudoku resuelto en las estadísticas. Devuelve lo que se añade a la felicitación."""
		datos = Estadisticas(archivos.ruta_estadisticas())
		partes = []
		if datos.registrar_resuelto(sudoku.forma.lado, sudoku.nivel, sudoku.segundos, sudoku.ayudas):
			# Translators: said after solving a sudoku faster than ever in that size and level.
			partes.append(_("It is your best time in this size and level!"))
		if sudoku.del_dia:
			racha = datos.registrar_del_dia(datetime.date.fromisoformat(sudoku.del_dia))
			partes.append(texto_racha(racha))
		try:
			datos.guardar()
		except OSError:
			log.error("No se pudieron guardar las estadísticas", exc_info=True)
		self._actualizar_menu()
		return " ".join(partes)

	def mostrar_atajos(self) -> None:
		"""Todas las teclas, del juego y de las lecciones. Se consultan con casillas creadas solo para eso."""
		contextos = {
			# NVDA solo acepta crear sus objetos con argumentos por nombre.
			atajos.Contexto.JUEGO: CeldaSudoku(cuadricula=None, fila=0, columna=0),
			atajos.Contexto.LECCION: CeldaLeccion(cuadricula=None, fila=0, columna=0),
		}
		wx.CallAfter(atajos.mostrar, contextos)

	def _borrar_progreso(self) -> bool:
		"""Cierra las lecciones y borra el progreso del curso y las estadísticas. Los sudokus a medias se quedan."""
		if self._curso is not None:
			self._curso.cerrar()
			# Se vuelve a crear al abrirlo, ya sin progreso.
			self._curso = None
		for ruta in (
			archivos.ruta_progreso(),
			archivos.ruta_estadisticas(),
			archivos.ruta_leccion_en_curso(),
		):
			archivos.borrar(ruta)
		return True

	# Sudoku del día.

	def sudoku_del_dia(self) -> None:
		wx.CallAfter(self._sudoku_del_dia)

	def _sudoku_del_dia(self) -> None:
		hoy = datetime.date.today()
		ventana = self._ventana
		if ventana is not None and ventana.sudoku.del_dia == hoy.isoformat() and not ventana.sudoku.resuelto:
			ventana.mostrar()
			return
		datos = Estadisticas(archivos.ruta_estadisticas())
		if datos.resuelto_hoy(hoy):
			MessageDialog.alert(
				# Translators: said when opening the sudoku of the day after solving it, as in "You already solved today's sudoku. You have solved it 3 days in a row. Come back tomorrow for a new one."
				_("You already solved today's sudoku. {streak} Come back tomorrow for a new one.").format(
					streak=texto_racha(datos.racha_actual(hoy)),
				),
				# Translators: title of the message about the sudoku of the day.
				_("Sudoku of the day"),
			)
			return
		ruta = archivos.ruta_guardado_del_dia()
		guardado = self._leer_guardado(ruta)
		if guardado is not None and guardado.del_dia == hoy.isoformat():
			self._abrir(guardado)
			return
		# El de otro día ya no se puede jugar.
		archivos.borrar(ruta)
		if self._generando:
			ui.message(_("A sudoku is already being prepared."))
			return
		respuesta = MessageDialog.ask(
			# Translators: asked before starting the sudoku of the day.
			_("How do you want to play today's sudoku?"),
			# Translators: title of the message about the sudoku of the day.
			_("Sudoku of the day"),
			# Translators: button to play the sudoku of the day with hints and clash warnings.
			yesLabel=_("&With help"),
			# Translators: button to play the sudoku of the day without hints or clash warnings.
			noLabel=_("With&out help"),
		)
		if respuesta not in (ReturnCode.YES, ReturnCode.NO):
			return
		ayudas = respuesta == ReturnCode.YES
		# Translators: said while the sudoku of the day is generated.
		self._generar(_("Preparing the sudoku of the day..."), lambda: diario.sudoku_del_dia(hoy, ayudas))

	@script(
		# Translators: description of the command that opens the sudoku of the day, shown in the Input gestures dialog.
		description=_("Opens the sudoku of the day"),
	)
	def script_sudoku_del_dia(self, gesture) -> None:
		self.sudoku_del_dia()

	@script(
		# Translators: description of the command that shows the statistics, shown in the Input gestures dialog.
		description=_("Shows your sudoku statistics"),
	)
	def script_estadisticas(self, gesture) -> None:
		wx.CallAfter(estadisticas.mostrar)

	def _al_cerrar_ventana(self) -> None:
		self._ventana = None
		self._actualizar_menu()

	# Integración con NVDA.

	def chooseNVDAObjectOverlayClasses(self, obj: NVDAObject, clsList: list[type[NVDAObject]]) -> None:
		# El panel que dibuja el tablero pasa el foco a la casilla virtual actual.
		if isinstance(obj, Window) and tablero_virtual.cuadricula_de_ventana(obj.windowHandle):
			clsList.insert(0, tablero_virtual.PanelCuadricula)

	@script(
		# Translators: description of the command that opens the sudoku board, shown in the Input gestures dialog.
		description=_("Opens the sudoku board: continues the unfinished sudoku or starts a new one"),
	)
	def script_abrir_tablero(self, gesture) -> None:
		if self._hay_para_continuar():
			self.continuar_sudoku()
		else:
			self.nuevo_sudoku()
