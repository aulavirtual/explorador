#!/usr/bin/env python
# -*- coding: utf-8 -*-

# widgets.py by:
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
import os

GROUPS = ("Seleccione un grupo", "1A", "1B", "1C", "2A", "2B", "2C", "3A", "3B")
SUBJECTS = ("Seleccione su materia", "Matematica", "Fisica", "Quimica", "Idioma Español", "Literatura", "Ingles", "Tecnologia", "F. Ciudadana","O. Vocacional", "Geografia", "Historia", "Dibujo", "Biologia", "Ed. Fisica", "Sexualidad",
"Informatica", "Cs. Fisicas", "TOC Administracion", "TOC Madera", "TOC Mecanica", "TOC Arte", "TOC Alimentacion", 
"TOC Electrotecnia", "TOC Tics")


class Combo(gtk.ComboBox):

    def __init__(self):
        self.liststore = gtk.ListStore(str)
        gtk.ComboBox.__init__(self, self.liststore)

        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)


class GroupChooser(Combo):

    def __init__(self):
        Combo.__init__(self)

        for group in GROUPS:
            self.liststore.append([group])

        self.set_active(0)

class Entry(gtk.Entry):

    def __init__(self, text):
        gtk.Entry.__init__(self, max=0)

        self.set_text(text)
        self.connect("focus-in-event", self._focus_in)
        self.connect("focus-out-event", self._focus_out)
        self.modify_font(pango.FontDescription("italic"))

        self._text = text

        self.show_all()

    def _focus_in(self, widget, event):
        if widget.get_text() == self._text:
            widget.set_text("")
            widget.modify_font(pango.FontDescription(""))

    def _focus_out(self, widget, event):
        if widget.get_text() == "":
            widget.set_text(self._text)
            widget.modify_font(pango.FontDescription("italic"))


class FileChooser(gtk.FileChooserDialog):
    
    def __init__(self, parent):
        gtk.FileChooserDialog.__init__(self, 
                                       "Seleccione un archivo",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
        self.set_default_response(gtk.RESPONSE_OK)

        response = self.run()
        if response == gtk.RESPONSE_OK:
             file = self.get_filename()           
             parent.set_file(file)
        
        self.destroy()
