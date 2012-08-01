import gobject
import gtk
import os

from documents import Documents
import utils


class Subjects(gtk.Table):
    __gsignals__ = {"selected": (gobject.SIGNAL_RUN_FIRST, None, [])}

    def __init__(self, notebook, documents):
        gtk.Table.__init__(self, columns=4)
        self.set_homogeneous(True)

        self._notebook = notebook
        self._documents = documents
        self._sftp = self._connect()      

        row = 0
        column = -1
        
        listdir = self._sftp.listdir(".")
        listdir.sort()
        for i in listdir:
            if not i.startswith("."):
                sw = SubjectWidget("", i)
                sw.connect("clicked", self._button_clicked)
                column += 1
                
                if column == self.props.n_columns:
                    row += 1
                    column = 0

                self.attach(sw, column, column + 1, row, row + 1)

    def _connect(self):
        sftp = utils.connect_to_server()
        return sftp

    def _button_clicked(self, widget, name):
	    self.emit('selected')
	    self._documents._activity._select_all.set_sensitive(True)
	    self._documents._activity._download.set_sensitive(True)
	    self._documents.set_path(self._sftp, name)
	    self._notebook.set_current_page(1)


class SubjectWidget(gtk.EventBox):
    __gsignals__ = {"clicked": (gobject.SIGNAL_RUN_FIRST, None, [str])}

    def __init__(self, image, name):
        gtk.EventBox.__init__(self)

        self.connect("button-press-event", self._clicked)

        box = gtk.VBox()
        self.subject_name = name
        
        icon = gtk.image_new_from_stock(gtk.STOCK_DIRECTORY, 
                                        gtk.ICON_SIZE_LARGE_TOOLBAR)
        label = gtk.Label(name)

        box.pack_start(icon, True)
        box.pack_start(label, False)

        self.add(box)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.set_border_width(10)

        self.show_all()
    
    def _clicked(self, widget, event):
        self.emit("clicked", self.subject_name)


if __name__ == "__main__":
    w = gtk.Window()
    scroll = gtk.ScrolledWindow()

    cosito = Documents()

    notebook = gtk.Notebook()
    wgt = Subjects(notebook, cosito)
    scroll.add_with_viewport(wgt)

    scroll1 = gtk.ScrolledWindow()
    scroll1.add_with_viewport(cosito)

    notebook.append_page(scroll1)
    notebook.append_page(scroll)
    notebook.set_property("show-tabs", False)

    w.add(notebook)
    w.show_all()
    notebook.set_current_page(1)
    gtk.main()
