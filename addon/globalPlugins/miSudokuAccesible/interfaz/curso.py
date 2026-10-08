# MiSudokuAccesible: sudoku accesible para NVDA.
# Copyright (C) 2026 Wilmer Rodríguez Vega <contacto@wilmer-rv.com>
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""«Aprender a jugar»: lista de lecciones, presentación, ejercicios y «Practicar»."""

import os
import random
import threading
from dataclasses import dataclass, field

import addonHandler
import languageHandler
import ui
import wx
from gui import guiHelper
from gui.message import displayDialogAsModal
from logHandler import log

from ..sudoku.curso.modelo import Curso, Ejercicio, Leccion, TipoEjercicio, cargar_curso, carpeta_de_idioma
from ..sudoku.curso.practica import TAMANO_RONDA, generar_ejercicio
from ..sudoku.curso.progreso import Progreso
from ..sudoku.curso.sesion import SesionEjercicio
from ..sudoku.grupos import FORMAS
from . import archivos, sonidos
from .ventana_leccion import VentanaLeccion, titulo_leccion

addonHandler.initTranslation()

# Respuesta del diálogo de lecciones cuando se pulsa «Practicar».
ID_PRACTICAR = wx.NewIdRef()


def texto_estado(leccion: Leccion, progreso: Progreso) -> str:
	total = len(leccion.ejercicios)
	hechos = sum(1 for e in leccion.ejercicios if progreso.superado(e.id))
	if hechos == total:
		# Translators: state of a completed lesson in the list of lessons.
		texto = _("Completed, {stars} of {total} stars.").format(
			stars=progreso.estrellas_de(leccion),
			total=leccion.estrellas_posibles,
		)
	elif hechos:
		# Translators: state of a lesson started but not finished, in the list of lessons.
		texto = _("In progress: {done} of {total} exercises.").format(done=hechos, total=total)
	else:
		# Translators: state of a lesson not started, in the list of lessons.
		texto = _("Pending.")
	mejor = progreso.mejor_practica(leccion.id)
	if mejor is not None:
		# Translators: best practice round of a lesson, shown in the list of lessons.
		practica = _("Best practice: {stars} of {total}.").format(stars=mejor, total=3 * TAMANO_RONDA)
		texto = f"{texto} {practica}"
	return texto


class DialogoLecciones(wx.Dialog):
	def __init__(self, curso: Curso, progreso: Progreso, seleccion: Leccion | None) -> None:
		# Translators: title of the list of lessons of the course.
		super().__init__(None, title=_("Learn to play"))
		self._lecciones = curso.lecciones
		textos = []
		for leccion in self._lecciones:
			texto = f"{leccion.id}. {leccion.titulo}. {texto_estado(leccion, progreso)}"
			bloque = curso.bloque_de(leccion)
			if bloque.lecciones[0] == leccion:
				# Translators: block heading before the first lesson of a block, as in "Block A, Getting to know sudoku."
				encabezado = _("Block {block}, {title}.").format(block=bloque.id, title=bloque.titulo)
				texto = f"{encabezado} {texto}"
			textos.append(texto)
		principal = wx.BoxSizer(wx.VERTICAL)
		ayudante = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.lista: wx.ListBox = ayudante.addLabeledControl(
			# Translators: label of the list of lessons.
			_("&Lessons:"),
			wx.ListBox,
			choices=textos,
			size=(560, 320),
		)
		botones = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: button that starts the selected lesson.
		empezar = botones.addButton(self, id=wx.ID_OK, label=_("&Start"))
		# Translators: button that starts a practice round of the selected lesson.
		self.practicar = botones.addButton(self, id=ID_PRACTICAR, label=_("&Practice"))
		# Translators: button that closes the list of lessons.
		botones.addButton(self, id=wx.ID_CANCEL, label=_("&Close"))
		ayudante.addDialogDismissButtons(botones, separated=True)
		principal.Add(ayudante.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.SetSizer(principal)
		principal.Fit(self)
		empezar.SetDefault()
		self.SetEscapeId(wx.ID_CANCEL)
		self.lista.SetSelection(self._indice_inicial(progreso, seleccion))
		self.lista.Bind(wx.EVT_LISTBOX_DCLICK, lambda evento: self.EndModal(wx.ID_OK))
		self.lista.Bind(wx.EVT_LISTBOX, lambda evento: self._actualizar())
		self.practicar.Bind(wx.EVT_BUTTON, lambda evento: self.EndModal(ID_PRACTICAR))
		self._actualizar()
		self.CentreOnScreen()
		self.lista.SetFocus()

	def _actualizar(self) -> None:
		"""«Practicar» solo está disponible en las lecciones de técnicas."""
		self.practicar.Enable(self.leccion_elegida().practica is not None)

	def _indice_inicial(self, progreso: Progreso, seleccion: Leccion | None) -> int:
		if seleccion is not None and seleccion in self._lecciones:
			return self._lecciones.index(seleccion)
		for indice, leccion in enumerate(self._lecciones):
			if not progreso.leccion_completada(leccion):
				return indice
		return 0

	def leccion_elegida(self) -> Leccion:
		return self._lecciones[max(0, self.lista.GetSelection())]


class DialogoPresentacion(wx.Dialog):
	"""Explicación de la lección. NVDA lee el texto al abrirse; NVDA+B lo vuelve a leer."""

	def __init__(self, leccion: Leccion, indice_inicial: int) -> None:
		super().__init__(None, title=titulo_leccion(leccion))
		parrafos = list(leccion.explicacion)
		cantidad = len(leccion.ejercicios)
		parrafos.append(
			ngettext(
				# Translators: said at the end of a lesson explanation.
				"This lesson has {count} exercise.",
				"This lesson has {count} exercises.",
				cantidad,
			).format(
				count=cantidad,
			),
		)
		if indice_inicial:
			# Translators: said when a lesson is resumed, as in "You will continue from exercise 3."
			parrafos.append(_("You will continue from exercise {number}.").format(number=indice_inicial + 1))
		principal = wx.BoxSizer(wx.VERTICAL)
		ayudante = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		for parrafo in parrafos:
			texto = wx.StaticText(self, label=parrafo)
			texto.Wrap(520)
			ayudante.addItem(texto)
		botones = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: button that starts the exercises of a lesson.
		empezar = botones.addButton(self, id=wx.ID_OK, label=_("&Start"))
		# Translators: button that goes back to the list of lessons.
		botones.addButton(self, id=wx.ID_CANCEL, label=_("&Back"))
		ayudante.addDialogDismissButtons(botones, separated=True)
		principal.Add(ayudante.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.SetSizer(principal)
		principal.Fit(self)
		empezar.SetDefault()
		self.SetEscapeId(wx.ID_CANCEL)
		self.CentreOnScreen()
		empezar.SetFocus()


@dataclass
class RondaPractica:
	"""Una ronda de «Practicar»: el ejercicio siguiente se prepara mientras se juega el actual."""

	leccion: Leccion
	numero: int = 0
	estrellas: list[int] = field(default_factory=list)
	preparado: Ejercicio | None = None
	# Si se está esperando el ejercicio preparado para mostrarlo.
	esperando: bool = True


class ControladorCurso:
	"""Lleva la lección o la práctica en curso. Solo hay una ventana de lección a la vez."""

	def __init__(self) -> None:
		self.curso = cargar_curso(carpeta_de_idioma(languageHandler.getLanguage()))
		self.progreso = Progreso(archivos.ruta_progreso())
		self.ventana: VentanaLeccion | None = None
		self.leccion: Leccion | None = None
		self.indice = 0
		self.ronda: RondaPractica | None = None

	def cerrar(self) -> None:
		# Una ronda que se está preparando ya no se mostrará.
		self.ronda = None
		if self.ventana is not None:
			self.ventana.cerrar_sin_preguntar()
			self.ventana = None

	def al_cerrar_ventana(self) -> None:
		self.ventana = None
		self.ronda = None

	# Lista y presentación.

	def abrir_lista(self, seleccion: Leccion | None = None) -> None:
		wx.CallAfter(self._abrir_lista, seleccion or self.leccion)

	def _abrir_lista(self, seleccion: Leccion | None) -> None:
		dialogo = DialogoLecciones(self.curso, self.progreso, seleccion)
		try:
			respuesta = displayDialogAsModal(dialogo)
			leccion = dialogo.leccion_elegida()
		finally:
			dialogo.Destroy()
		if respuesta == ID_PRACTICAR:
			self._practicar(leccion)
		elif respuesta == wx.ID_OK:
			self._presentar(leccion)

	def _presentar(self, leccion: Leccion) -> None:
		indice = self.progreso.primer_pendiente(leccion)
		dialogo = DialogoPresentacion(leccion, indice)
		try:
			respuesta = displayDialogAsModal(dialogo)
		finally:
			dialogo.Destroy()
		if respuesta != wx.ID_OK:
			self._abrir_lista(leccion)
			return
		self._empezar(leccion, indice)

	def siguiente_leccion(self) -> None:
		if self.leccion is None:
			return
		siguiente = self.curso.siguiente(self.leccion)
		if siguiente is not None:
			wx.CallAfter(self._presentar, siguiente)

	# Ejercicios de la lección.

	def _empezar(self, leccion: Leccion, indice: int) -> None:
		self.cerrar()
		self.leccion = leccion
		self.indice = indice
		sesion = self._sesion(leccion.ejercicios[indice])
		self.ventana = VentanaLeccion(self, leccion, sesion, indice, len(leccion.ejercicios))
		self.ventana.mostrar()

	def _sesion(self, ejercicio: Ejercicio) -> SesionEjercicio:
		"""Un ejercicio de la lección. Si es un sudoku entero que quedó a medias, sigue donde estaba."""
		sesion = SesionEjercicio(ejercicio)
		ruta = archivos.ruta_leccion_en_curso()
		if sesion.se_guarda and os.path.isfile(ruta):
			try:
				sesion.continuar(archivos.leer(ruta))
			except OSError:
				log.debugWarning("No se pudo leer la lección en curso", exc_info=True)
		return sesion

	def guardar_en_curso(self) -> None:
		"""Tras cada cambio o pista de un sudoku entero de una lección (no en la práctica)."""
		ventana = self.ventana
		if ventana is None or ventana.practica or not ventana.sesion.se_guarda:
			return
		try:
			archivos.escribir(archivos.ruta_leccion_en_curso(), ventana.sesion.a_json())
		except OSError:
			log.error("No se pudo guardar la lección en curso", exc_info=True)

	def al_superar(self, mensaje: str) -> None:
		ventana = self.ventana
		if ventana is None:
			return
		felicitacion = f"{mensaje}. {ventana.sesion.texto_superado()}"
		if self.ronda is not None:
			self._superar_practica(self.ronda, ventana, felicitacion)
			return
		leccion = self.leccion
		if leccion is None:
			return
		sesion = ventana.sesion
		self.progreso.registrar(sesion.principal.id, sesion.estrellas)
		self._guardar_progreso()
		if sesion.principal.tipo is TipoEjercicio.COMPLETAR:
			archivos.borrar(archivos.ruta_leccion_en_curso())
		siguiente = self.indice + 1
		if siguiente < len(leccion.ejercicios):
			sonidos.reproducir(sonidos.EXITO)
			ui.message(felicitacion)
			self.indice = siguiente
			ventana.cargar(self._sesion(leccion.ejercicios[siguiente]), siguiente)
			ui.message(ventana.texto_instruccion())
			return
		sonidos.reproducir(sonidos.RESUELTO)
		ui.message(felicitacion)
		ui.message(self._texto_final(leccion))

	def _guardar_progreso(self) -> None:
		try:
			self.progreso.guardar()
		except OSError:
			log.error("No se pudo guardar el progreso del curso", exc_info=True)

	def _texto_final(self, leccion: Leccion) -> str:
		partes = [
			# Translators: said when a lesson is finished, as in "You finished lesson 1! You have 11 of 12 stars."
			_("You finished lesson {id}! You have {stars} of {total} stars.").format(
				id=leccion.id,
				stars=self.progreso.estrellas_de(leccion),
				total=leccion.estrellas_posibles,
			),
		]
		bloque = self.curso.bloque_de(leccion)
		if bloque.lecciones[-1] == leccion:
			partes.append(bloque.mensaje_final)
		if self.curso.siguiente(leccion) is not None:
			# Translators: said at the end of a lesson.
			partes.append(_("Open the menu with the Applications key to go on to the next lesson."))
		return " ".join(partes)

	# Práctica.

	def practicar(self, leccion: Leccion) -> None:
		wx.CallAfter(self._practicar, leccion)

	def _practicar(self, leccion: Leccion) -> None:
		if leccion.practica is None:
			return
		self.leccion = leccion
		self.ronda = RondaPractica(leccion)
		# Translators: said while the first exercise of a practice round is prepared.
		ui.message(_("Preparing the practice..."))
		self._preparar(self.ronda)

	def _preparar(self, ronda: RondaPractica) -> None:
		"""Genera el siguiente ejercicio de la ronda en otro hilo: puede tardar un par de segundos."""
		practica = ronda.leccion.practica
		assert practica is not None
		id_ejercicio = f"practica-{ronda.leccion.id}-{len(ronda.estrellas) + 1}"

		def generar() -> None:
			try:
				ejercicio = generar_ejercicio(
					id_ejercicio,
					practica.objetivo,
					FORMAS[practica.lado],
					random.Random(),
				)
			except Exception:
				log.error("No se pudo generar el ejercicio de práctica", exc_info=True)
				ejercicio = None
			wx.CallAfter(self._al_preparar, ronda, ejercicio)

		threading.Thread(target=generar, daemon=True).start()

	def _al_preparar(self, ronda: RondaPractica, ejercicio: Ejercicio | None) -> None:
		if ronda is not self.ronda:
			return
		if ejercicio is None:
			self.ronda = None
			# Translators: reported when a practice exercise could not be prepared.
			ui.message(_("The practice could not be prepared. Please try again."))
			return
		ronda.preparado = ejercicio
		if ronda.esperando:
			ronda.esperando = False
			self._mostrar_practica(ronda)

	def _mostrar_practica(self, ronda: RondaPractica) -> None:
		ejercicio = ronda.preparado
		assert ejercicio is not None
		ronda.preparado = None
		sesion = SesionEjercicio(ejercicio)
		ventana = self.ventana
		if ventana is None or not ventana.practica or ventana.leccion is not ronda.leccion:
			if ventana is not None:
				ventana.cerrar_sin_preguntar()
			# Cerrar la ventana anterior olvida la ronda: se recupera.
			self.ronda = ronda
			self.ventana = VentanaLeccion(
				self,
				ronda.leccion,
				sesion,
				ronda.numero,
				TAMANO_RONDA,
				practica=True,
			)
			self.ventana.mostrar()
		else:
			ventana.cargar(sesion, ronda.numero)
			ui.message(ventana.texto_instruccion())
		if ronda.numero + 1 < TAMANO_RONDA:
			self._preparar(ronda)

	def _superar_practica(self, ronda: RondaPractica, ventana: VentanaLeccion, felicitacion: str) -> None:
		ronda.estrellas.append(ventana.sesion.estrellas)
		ronda.numero += 1
		if ronda.numero < TAMANO_RONDA:
			sonidos.reproducir(sonidos.EXITO)
			ui.message(felicitacion)
			if ronda.preparado is not None:
				self._mostrar_practica(ronda)
			else:
				ronda.esperando = True
				# Translators: said while the next practice exercise is still being prepared.
				ui.message(_("Preparing the next exercise..."))
			return
		total = sum(ronda.estrellas)
		self.progreso.registrar_practica(ronda.leccion.id, total)
		self._guardar_progreso()
		self.ronda = None
		sonidos.reproducir(sonidos.RESUELTO)
		ui.message(felicitacion)
		mejor = self.progreso.mejor_practica(ronda.leccion.id)
		ui.message(
			_(
				# Translators: said at the end of a practice round, as in "You finished the practice round with 13 of 15 stars. Your best: 14. Open the menu to play another round."
				"You finished the practice round with {stars} of {total} stars. Your best: {best}. "
				"Open the menu to play another round.",
			).format(stars=total, total=3 * TAMANO_RONDA, best=mejor),
		)
