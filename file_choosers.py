#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#   file_choosers.py by/por:
#   Daniel Francis <santiago.danielfrancis@gmail.com>
#   Agustin Zubiaga <aguzubiaga97@gmail.com>
#   Sugarlabs - CeibalJAM! - Uruguay

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

from sugar import mime
from sugar.graphics.objectchooser import ObjectChooser

OPEN_FROM_JOURNAL = -12


def open_from_journal(button, filechooser, activity=None):
        if filechooser:
                chooser = ObjectChooser(parent=filechooser,
                                        what_filter=mime.GENERIC_TYPE_TEXT)
        else:
                chooser = ObjectChooser(parent=activity,
                                        what_filter=mime.GENERIC_TYPE_TEXT)
        result = chooser.run()
        chooser.destroy()
        if result == gtk.RESPONSE_ACCEPT:
                jobject = chooser.get_selected_object()
                path = str(jobject.get_file_path())
        else:
                path = None
        if filechooser:
                filechooser.path = path
                filechooser.response(OPEN_FROM_JOURNAL)
        else:
                activity.open_file(None, from_journal=path)


def open_file_dialog():
        dialog = gtk.FileChooserDialog(_("Open..."),
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name(_("All files"))
        filter.add_pattern("*")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name(_("All text files"))
        filter.add_mime_type("text/*")
        dialog.add_filter(filter)

        lang_ids = langs
        for i in lang_ids:
                lang = langsmanager.get_language(i)
                filter = gtk.FileFilter()
                filter.set_name(lang.get_name())
                for m in lang.get_mime_types():
                        filter.add_mime_type(m)
                dialog.add_filter(filter)

        open_from_journal_button = gtk.Button(_("Open from Journal"))
        open_from_journal_button.connect("clicked", open_from_journal, dialog)
        open_from_journal_button.show()
        dialog.set_extra_widget(open_from_journal_button)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
                to_return = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
                to_return = None
        elif response == OPEN_FROM_JOURNAL:
                dialog.destroy()
                return dialog.path, False
        dialog.destroy()
        return to_return, True


def confirm_overwrite(widget):
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION)
        dialog.add_buttons(gtk.STOCK_NO, gtk.RESPONSE_CANCEL,
                           gtk.STOCK_YES, gtk.RESPONSE_ACCEPT)
        dialog.set_markup("<b>%s</b>" % _("This file name already exists"))
        dialog.format_secondary_text(_("Overwrite the file?"))
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_ACCEPT:
                return gtk.FILE_CHOOSER_CONFIRMATION_ACCEPT_FILENAME
        else:
                return gtk.FILE_CHOOSER_CONFIRMATION_SELECT_AGAIN


def save_file_dialog():
        dialog = gtk.FileChooserDialog(_("Save..."),
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_do_overwrite_confirmation(True)
        dialog.connect("confirm-overwrite", confirm_overwrite)

        filter = gtk.FileFilter()
        filter.set_name(_("All files"))
        filter.add_pattern("*")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name(_("All text files"))
        filter.add_mime_type("text/*")
        dialog.add_filter(filter)

        lang_ids = langs
        for i in lang_ids:
                lang = langsmanager.get_language(i)
                filter = gtk.FileFilter()
                filter.set_name(lang.get_name())
                for m in lang.get_mime_types():
                        filter.add_mime_type(m)
                dialog.add_filter(filter)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
                to_return = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
                to_return = None
        dialog.destroy()
        return to_return
