import gtk
import sys
import gobject
import threading
import pango
import utils

from sugar.activity import activity
from sugar.activity.widgets import ActivityButton
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.icon import Icon
from sugar.graphics.alert import Alert

from subjects import Subjects
from documents import Documents

GROUPS = ('1A', '1B', '1C', '2A', '2B', '2C', '3A', '3B')


class Explorer(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle, True)

        # ToolbarBox:

        toolbarbox = ToolbarBox()
        activitybutton = ActivityButton(self)
        toolbarbox.toolbar.insert(activitybutton, 0)

        separator = gtk.SeparatorToolItem()
        toolbarbox.toolbar.insert(separator, -1)

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
        separator.set_expand(True)
        separator.set_draw(False)
        toolbarbox.toolbar.insert(separator, -1)

        stopbtn = StopButton(self)
        toolbarbox.toolbar.insert(stopbtn, -1)

        self.set_toolbar_box(toolbarbox)
        self._one_alert = None

        # Canvas
        self._canvas = gtk.EventBox()
        
        self.set_canvas(self._canvas)
        self.show_all()
        if not utils.get_group():
		    self.choose_group()
        else:
		    self._do_canvas()

    def choose_group(self):
        vbox = gtk.VBox()
        vbox.set_border_width(20)
        
        title = gtk.Label('Registrate en Aula Virtual')
        title.modify_font(pango.FontDescription('bold 25'))
        vbox.pack_start(title, False, padding=40)
        
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, padding=10)
        
        label = gtk.Label("Nombre: ")
        hbox.pack_start(label, False, padding=10)
        
        entry = gtk.Entry()
        hbox.pack_start(entry, True, padding=0)
        
        hbox1 = gtk.HBox()
        hbox1.set_border_width(20)
        
        label = gtk.Label("Apellido:  ")
        hbox1.pack_start(label, False, padding=0)
        
        entry = gtk.Entry()
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
            
        accept = gtk.Button('Aceptar')
        accept.connect('clicked', self._accept_clicked, combo, entry, vbox)
        box = gtk.HBox()
        box.pack_end(accept, False)
        vbox.pack_start(box, False)
        
        self._canvas.add(vbox)
        self.show_all()
        
    def _accept_clicked(self, widget, combo, entry, vbox):
        group = GROUPS[combo.get_active()]
        utils.GROUP = group
        vbox.destroy()
        self._do_canvas()
        utils.save_me(self._subjects._sftp, group, entry.get_text())
        
    def _go_up_clicked(self, widget):
        self._notebook.set_current_page(0)
        self._goup.set_sensitive(False)
        
    def _select_all_clicked(self, widget):
        self._documents.select_all()

    def _do_canvas(self):
		#try:
		    scroll_documents = gtk.ScrolledWindow()
		    scroll_documents.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		    self._documents = Documents(self)

		    self._notebook = gtk.Notebook()
		    self._subjects = Subjects(self._notebook, self._documents)
		    self._subjects.connect('selected', lambda w: self._goup.set_sensitive(True))
		    scroll_documents.add_with_viewport(self._documents)

		    scroll_subjects = gtk.ScrolledWindow()
		    scroll_subjects.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		    scroll_subjects.add_with_viewport(self._subjects)

		    self._notebook.append_page(scroll_subjects)
		    self._notebook.append_page(scroll_documents)
		    self._notebook.set_property("show-tabs", False)

		    self._canvas.add(self._notebook)
		    self._canvas.show_all()

		    self._notebook.set_current_page(0)
		    
		#except:
		#	self._loading_label.hide()
				
		#	alert = Alert()

		#	alert.props.title = 'Error al conectarse'
		#	alert.props.msg = err#'Por favor conectate a la Red AulaVirtual'

		#	ok_icon = Icon(icon_name='dialog-ok')
		#	alert.add_button(gtk.RESPONSE_OK, 'Salir', ok_icon)
		#	ok_icon.show()

		#	alert.connect('response', lambda w, r: sys.exit())

		#	self.add_alert(alert)

		
    def get_alert(self):
        if not self._one_alert:
            self._one_alert = Alert()
            self.add_alert(self._one_alert)
	    
        return self._one_alert

