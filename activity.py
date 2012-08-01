import gtk
import sys
import gobject
import threading

from sugar.activity import activity
from sugar.activity.widgets import ActivityButton
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.icon import Icon
from sugar.graphics.alert import Alert

from subjects import Subjects
from documents import Documents


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
        
        self._loading_label = gtk.Label('<span font_desc="30"><i>%s</i></span>' % 'Cargando...')
        self._loading_label.set_use_markup(True)
        self._canvas.add(self._loading_label)

        self.set_canvas(self._canvas)
        self.show_all()
        self._do_canvas()
        
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

		    self._loading_label.destroy()
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

