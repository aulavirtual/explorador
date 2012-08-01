import gobject
import gtk
import pango
from sugar.graphics import style
from sugar.graphics.toolbutton import ToolButton	
from sugar.graphics.icon import Icon
from sugar import mime
from sugar import profile


class _DialogWindow(gtk.Window):

    # A base class for a modal dialog window.
    def __init__(self, icon_name, title):	
        super(_DialogWindow, self).__init__()

        self.set_border_width(style.LINE_WIDTH)
        width = gtk.gdk.screen_width() - style.GRID_CELL_SIZE * 2
        height = gtk.gdk.screen_height() - style.GRID_CELL_SIZE * 3
        self.set_size_request(width, height)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_decorated(False)
        self.set_resizable(False)
        #self.set_modal(True)
        vbox = gtk.VBox()
        self.add(vbox)
        toolbar = _DialogToolbar(icon_name, title)
        toolbar.connect('stop-clicked', self._stop_clicked_cb)
        vbox.pack_start(toolbar, False)
        
        eventbox = gtk.EventBox()
        eventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))

        self.content_vbox = gtk.VBox()
        self.content_vbox.set_border_width(style.DEFAULT_SPACING)
        eventbox.add(self.content_vbox)
        eventbox.show_all()
        vbox.add(eventbox)
        self.connect('realize', self._realize_cb)
        
    def _stop_clicked_cb(self, source):
        self.destroy()
    def _realize_cb(self, source):
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.set_accept_focus(True)
        
class _DialogToolbar(gtk.Toolbar):
    # Displays a dialog window's toolbar, with title, icon, and close box.
    __gsignals__ = {
        'stop-clicked': (gobject.SIGNAL_RUN_LAST, None, ()),	
    }
    def __init__(self, icon_name, title):	
        super(_DialogToolbar, self).__init__()

        if icon_name is not None:
            sep = gtk.SeparatorToolItem()
            sep.set_draw(False)	
            self._add_widget(sep)
            icon = Icon()
            icon.set_from_icon_name(icon_name, gtk.ICON_SIZE_LARGE_TOOLBAR)
            self._add_widget(icon)
            
        label = gtk.Label('  ' + title)
        self._add_widget(label)
        self._add_separator(expand=True)
        stop = ToolButton(icon_name='dialog-cancel')
        stop.set_tooltip('Salir')
        stop.connect('clicked', self._stop_clicked_cb)
        self.add(stop)

    def _add_separator(self, expand=False):
        separator = gtk.SeparatorToolItem()
        separator.set_expand(expand)
        separator.set_draw(False)
        self.add(separator)

    def _add_widget(self, widget):
        tool_item = gtk.ToolItem()
        tool_item.add(widget)
        self.add(tool_item)

    def _stop_clicked_cb(self, button):
        self.emit('stop-clicked')


class InfoDialog(_DialogWindow):	
    __gtype_name__ = 'InfoDialog'
    __gsignals__ = {"save-document": (gobject.SIGNAL_RUN_FIRST, None, ())}
	
    def __init__(self, title, desc, teacher, subject, mimetype):
        super(InfoDialog, self).__init__("info",
                                            'Informacion del documento')
       
        hbox = gtk.HBox()
        self.content_vbox.pack_start(hbox, True)
        
        previewbox = gtk.VBox() 
        preview = Icon(pixel_size=300)
        preview.props.icon_name = mime.get_mime_icon(mimetype)
        preview.props.xo_color = profile.get_color()
        previewbox.pack_start(preview, False)
        hbox.pack_start(previewbox, False, padding=5)
        
        vbox = gtk.VBox()
        hbox.pack_end(vbox, True, padding=20)
        
        title_label = gtk.Label('<span font_desc="15"><b>%s</b></span>' % title)
        title_label.set_use_markup(True)
        vbox.pack_start(title_label, False)

        desc_box = gtk.VBox()
        desc_label = gtk.Label('<i>%s</i>' % desc)
        desc_label.set_use_markup(True)
        desc_label.set_line_wrap(True)
        desc_box.pack_start(desc_label, False, padding=30)
        vbox.pack_start(desc_box, True)
        
        box = gtk.HBox()
        teacher_label = gtk.Label('%s - %s' % (teacher, subject))
        box.pack_start(teacher_label, False)
        
        bbox = gtk.HBox()
        self.content_vbox.pack_end(bbox, False)
        self.content_vbox.pack_end(box, False)
        
        btn_save = gtk.Button(stock=gtk.STOCK_SAVE)
        btn_save.connect('clicked', lambda w: self.emit('save-document'))
        bbox.pack_end(btn_save, False)

        self.show_all()
        
