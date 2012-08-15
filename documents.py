# -*- coding: UTF-8 -*-

import threading
import gtk
import gobject
import os

import utils
from dialogs import InfoDialog
from sugar.graphics import style
from sugar.graphics.icon import Icon
from sugar import profile
from sugar import mime


class Documents(gtk.EventBox):

    def __init__(self, activity):
        gtk.EventBox.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, style.COLOR_WHITE.get_gdk_color())

        self._activity = activity
        self._all_selected = False
        self._vbox = gtk.VBox()
        self.add(self._vbox)
        
        activity._goup.connect("clicked", self._go_up_clicked)
        activity._download.connect("clicked", self._download)

        self.show_all()

    def select_all(self, *kwargs):
        for widget in self._vbox.get_children():
            if not self._all_selected:
                widget.select()
            else:
                widget.unselect()
                
        self._all_selected = not self._all_selected
        
    def _go_up_clicked(self, widget):
        self._all_selected = False 
        self._activity._select_all.set_sensitive(False)
        self._activity._download.set_sensitive(False)

    def clear(self):
        self._selection = []
        for widget in self._vbox.get_children():
            self._vbox.remove(widget)
            widget.destroy()

    def set_path(self, sftp, subject="."):
        self.clear()
        self._sftp = sftp
        self._subject = subject
        self._documents = []
        if not utils.get_documents(sftp, subject):
            label = gtk.Label('<span font_desc="12"><i>%s</i></span>' % 'No hay documentos')
            label.set_use_markup(True)
            self._vbox.pack_start(label, False, True, 5)
        for document in utils.get_documents(sftp, subject):
            mimetype = utils.get_info(self._sftp, self._subject, document, only_mime=True)
            item = ListItem(document, mimetype)
            item.connect("show-info", self._show_info)
            item.connect("selected", self._selected)
            item.connect("unselected", self._unselected)
            self._vbox.pack_start(item, False, True, 5)
            item.show()
        self._activity.show_all()

    def _show_info(self, widget):
        desc, teacher, mimetype = utils.get_info(self._sftp, self._subject, widget.title)

        dialog = InfoDialog(widget.title, desc, teacher, self._subject, mimetype)
        dialog.connect('save-document', lambda w: utils.save_document(
                                 self._sftp, self._subject, widget.title, mimetype))
                                 
    def _selected(self, widget):
        self._selection.append(widget)
        
    def _unselected(self, widget):
        self._selection.remove(widget)
                                 
    def _download(self, widget):
        count = 0
        for document in self._selection:
            count += 1
            alert = self._activity.get_alert()

            alert.props.title = 'Descargando documento(s)...'
            alert.props.msg = 'Se está descargando el/los documento(s)'

            alert.show()
            utils.save_document(
            self._sftp, self._subject, document.title, document.mimetype)
        alert.props.title = '¡Descarga completa!'
        alert.props.msg = 'Todos archivos se han descargado'
        
        ok_icon = Icon(icon_name='dialog-ok')
        alert.add_button(gtk.RESPONSE_OK, 'Ok', ok_icon)
        ok_icon.show()

        alert.connect('response', lambda w, r: self._activity.remove_alert(w))
        
        alert.show()
        self._alert = None
        
        
class ListItem(gtk.HBox):
    __gsignals__ = {"show-info": (gobject.SIGNAL_RUN_FIRST, None, ()),
                    'selected': (gobject.SIGNAL_RUN_FIRST, None, ()),
                    'unselected': (gobject.SIGNAL_RUN_FIRST, None, ())}

    def __init__(self, title, mimetype):
        gtk.HBox.__init__(self)

        self._checkbutton = gtk.CheckButton()
        self._checkbutton.connect('toggled', self._toggled)
        label = gtk.Label("<b>%s</b>" % (title))
        label.set_use_markup(True)
        icon = Icon(pixel_size=52)
        icon.props.icon_name = mime.get_mime_icon(mimetype)
        icon.props.xo_color = profile.get_color()
        button = gtk.ToolButton()
        button.connect('clicked', lambda w: self.emit('show-info'))
        icon_info = Icon(pixel_size=24)
        icon_info.props.icon_name = 'info-small'
        button.set_icon_widget(icon_info)
        self.pack_start(self._checkbutton, False, True, 5)
        self.pack_start(icon, False, True, 5)
        self.pack_start(label, False, True, 5)
        self.pack_end(button, False, True, 5)
        self.title = title
        self.mimetype = mimetype

        self.show_all()

    def _toggled(self, widget):
        if widget.get_active():
            self.emit('selected')
        else:
            self.emit('unselected')
            
    def select(self):
        self._checkbutton.set_active(True)
        self.emit('selected')
        
    def unselect(self):
        self._checkbutton.set_active(False)
        self.emit('unselected')
    
        
            

