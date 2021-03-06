#!/usr/bin/env python
# -*- coding: utf-8 -*-

# activity.py by:
#    Agustin Zubiaga <aguz@sugarlabs.org>
#    Cristhofer Travieso <cristhofert97@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import pango
import utils
import widgets
import documents

from sugar.activity import activity
from sugar.activity.widgets import ActivityButton
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.radiotoolbutton import RadioToolButton
from sugar.graphics.alert import Alert
from sugar.graphics.objectchooser import ObjectChooser
from sugar import mime

from subjects import Subjects
from documents import Documents

GROUPS = ('1A', '1B', '1C', '2A', '2B', '2C', '3A', '3B')


class Explorer(activity.Activity):
    '''Es la clase que crea la actividad'''
    def __init__(self, handle):
        activity.Activity.__init__(self, handle, True)

        # ToolbarBox:

        toolbarbox = ToolbarBox()
        activitybutton = ActivityButton(self)
        toolbarbox.toolbar.insert(activitybutton, 0)

        separator = gtk.SeparatorToolItem()
        toolbarbox.toolbar.insert(separator, -1)

        explorer_btn = RadioToolButton()
        explorer_btn.set_tooltip('Explorador')
        explorer_btn.props.icon_name = 'activity-explorer'
        toolbarbox.toolbar.insert(explorer_btn, -1)

        self._goup = ToolButton('to-subjects')
        self._goup.connect('clicked', self._go_up_clicked)
        self._goup.set_tooltip('Ver Materias')
        self._goup.set_accelerator("<Shift><M>")
        self._goup.set_sensitive(False)
        toolbarbox.toolbar.insert(self._goup, -1)

        self._select_all = ToolButton('select-all')
        self._select_all.set_tooltip('Seleccionar todo')
        self._select_all.connect("clicked", self._select_all_clicked)
        self._select_all.set_sensitive(False)
        toolbarbox.toolbar.insert(self._select_all, -1)

        self._download = ToolButton('download')
        self._download.set_tooltip('Descargar')
        self._download.set_sensitive(False)
        toolbarbox.toolbar.insert(self._download, -1)

        separator = gtk.SeparatorToolItem()
        toolbarbox.toolbar.insert(separator, -1)

        homework_btn = RadioToolButton()
        homework_btn.set_tooltip('Tareas Domiciliarias')
        homework_btn.props.icon_name = 'homework'
        homework_btn.props.group = explorer_btn

        toolbarbox.toolbar.insert(homework_btn, -1)

        open_btn = ToolButton()
        open_btn.set_tooltip('Seleccionar tarea')
        open_btn.props.icon_name = 'open-from-journal'
        open_btn.set_sensitive(False)
        open_btn.connect("clicked", self._select_hw_from_journal)
        toolbarbox.toolbar.insert(open_btn, -1)

        self._send = ToolButton()
        self._send.set_tooltip('Enviar tarea')
        self._send.connect('clicked', self._send_hw_to_server)
        self._send.props.icon_name = 'document-send'
        self._send.set_sensitive(False)
        toolbarbox.toolbar.insert(self._send, -1)

        homework_btn.connect('clicked', self.homework_btn_cb, open_btn)
        explorer_btn.connect('clicked', self.explorer_btn_cb, open_btn)

        separator = gtk.SeparatorToolItem()
        separator.set_expand(True)
        separator.set_draw(False)
        toolbarbox.toolbar.insert(separator, -1)

        stopbtn = StopButton(self)
        toolbarbox.toolbar.insert(stopbtn, -1)

        self.set_toolbar_box(toolbarbox)
        self._one_alert = None

        # Canvas
        self._canvas = gtk.EventBox()
        self._name = ''
        self._last_name = ''
        self._hw_title = ''
        self._hw_description = ''
        self._hw_path = ''
        self._hw_mimetype = ''

        self.set_canvas(self._canvas)
        self.show_all()
        if not utils.get_group():
            self.choose_group()
        else:
            self._do_canvas()

    def homework_btn_cb(self, button, open_btn):
        '''Se ejecuta cuando se hace click en el boton
        de tareas domiciliarias, se encarga de cambiar de pagina'''
        self._notebook.set_current_page(2)
        self._goup.set_sensitive(False)
        self._select_all.set_sensitive(False)
        self._download.set_sensitive(False)
        open_btn.set_sensitive(True)
        self._send.set_sensitive(False)

    def explorer_btn_cb(self, widget, open_btn):
        '''Se ejecuta cuando se hace click en el boton
        del explorador, se encarga de cambiar de pagina'''
        self._notebook.set_current_page(0)
        open_btn.set_sensitive(False)
        self._send.set_sensitive(False)

    def _select_hw_from_journal(self, widget):
        '''Abre un selector de objetos del diario'''
        chooser = ObjectChooser()
        response = chooser.run()

        if response == gtk.RESPONSE_ACCEPT:
            jobject = chooser.get_selected_object()
            self._hw_path = str(jobject.get_file_path())
            self._notebook.set_current_page(-1)
            self._send.set_sensitive(True)
            self._hw_title.set_text(jobject.get_metadata()["title"])
            self._hw_mimetype = mime.get_for_file(self._hw_path)

    def _send_hw_to_server(self, widget):
        '''Envia las tareas domiciliarias'''
        _buffer = self._hw_description.get_buffer()
        start = _buffer.get_start_iter()
        end = _buffer.get_end_iter()
        comments = _buffer.get_text(start, end)

        utils.send_homework(self._subjects._sftp, 
                                           self._subjects_selector.\
                                           get_active_text(),
                                           self._hw_path,
                                           self._hw_title.get_text(), 
                                           comments,  self._hw_mimetype)

        self._notebook.set_current_page(2)

    def _set_text(self, widget, name=True):
        if name:
            self._name = widget.get_text()
        else:
            self._last_name = widget.get_text()

    def _do_homework_canvas(self):
        '''Arma el canvas para la tareas domiciliarias '''
        main_container = gtk.VBox()

        self._hw_title = widgets.Entry('Escriba el titulo aqui')
        main_container.pack_start(self._hw_title, False, True, 0)

        label = gtk.Label('Comentarios:')
        main_container.pack_start(label, False, True, 10)

        self._hw_description = gtk.TextView()
        self._hw_description.set_property('wrap-mode', gtk.WRAP_WORD_CHAR)
        main_container.pack_start(self._hw_description, True, True, 5)

        hbox = gtk.HBox()
        main_container.pack_start(hbox, False, True)
        self._subjects_selector = widgets.SubjectChooser()
        hbox.pack_start(self._subjects_selector, False, True, 0)

        return main_container

    def choose_group(self):
        '''Selector de los grupos'''
        vbox = gtk.VBox()
        vbox.set_border_width(20)

        title = gtk.Label('Registrate en Aula Virtual')
        title.modify_font(pango.FontDescription('bold 25'))
        vbox.pack_start(title, False, padding=40)

        note = gtk.Label('<span foreground="#FF0000"><i>\
                      * Por favor ingresa los datos correctamente.</i></span>')
        note.set_use_markup(True)
        vbox.pack_start(note, False, True, padding=5)

        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, padding=10)

        label = gtk.Label("Nombre: ")
        hbox.pack_start(label, False, padding=10)

        entry = gtk.Entry()
        entry.connect('changed', self._set_text)
        hbox.pack_start(entry, True, padding=0)

        hbox1 = gtk.HBox()
        hbox1.set_border_width(20)

        label = gtk.Label("Apellido:  ")
        hbox1.pack_start(label, False, padding=0)

        entry = gtk.Entry()
        entry.connect('changed', self._set_text, False)
        hbox1.pack_start(entry, True, padding=0)

        vbox.pack_start(hbox1, False, padding=10)

        hbox2 = gtk.HBox()
        vbox.pack_start(hbox2, False, padding=10)

        label_combo = gtk.Label("Elige tu grupo: ")
        hbox2.pack_start(label_combo, False, True, padding=10)

        combo = gtk.ComboBox()
        liststore = gtk.ListStore(str)
        combo.set_model(liststore)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        hbox2.pack_start(combo, False, True, padding=10)

        for group in GROUPS:
            liststore.append([group])
        combo.set_active(0)

        accept = gtk.Button('Aceptar')
        accept.connect('clicked', self._accept_clicked, combo, entry, vbox)
        box = gtk.HBox()
        box.pack_end(accept, False)
        vbox.pack_start(box, False)

        self._canvas.add(vbox)
        self.show_all()

    def _accept_clicked(self, widget, combo, entry, vbox):
        '''Se encarga de guardar la informacion de 
        la maquina en el sevidor'''
        group = GROUPS[combo.get_active()]
        utils.GROUP = group
        vbox.destroy()
        self._do_canvas()
        utils.save_me(self._subjects._sftp,
                      group,
                      '%s %s' % (self._name, self._last_name))

    def _go_up_clicked(self, widget):
        '''Mustra la lista de materias'''
        self._notebook.set_current_page(0)
        self._goup.set_sensitive(False)
        self._select_all.set_sensitive(False)
        self._download.set_sensitive(False)

    def _select_all_clicked(self, widget):
        '''Selecciona todo'''
        self._documents.select_all()

    def _do_canvas(self):
        '''Crea el canvas principal'''
        scroll_documents = gtk.ScrolledWindow()
        scroll_documents.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self._documents = Documents(self)

        self._notebook = gtk.Notebook()
        self._subjects = Subjects(self._notebook, self._documents, 
                                  self._go_up_clicked)
        self._subjects.connect('selected',
                               lambda w: self._goup.set_sensitive(True))
        scroll_documents.add_with_viewport(self._documents)

        scroll_subjects = gtk.ScrolledWindow()
        scroll_subjects.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll_subjects.add_with_viewport(self._subjects)

        self._notebook.append_page(scroll_subjects)
        self._notebook.append_page(scroll_documents)
        self._notebook.append_page(documents.HomeWorks(self._subjects._sftp))
        self._notebook.append_page(self._do_homework_canvas())
        self._notebook.set_property("show-tabs", False)

        self._canvas.add(self._notebook)
        self._canvas.show_all()

        self._notebook.set_current_page(0)

    def get_alert(self):
        '''Devuelve la alerta'''
        if not self._one_alert:
            self._one_alert = Alert()
            self.add_alert(self._one_alert)

        return self._one_alert
