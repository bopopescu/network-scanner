# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
import sys
import gtk
from xml.dom import minidom

from higwidgets.higboxes import HIGHBox
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higbuttons import HIGButton

from umit.gui.FileChoosers import AllFilesFileChooserDialog

from umit.core.NmapOptions import NmapOptions
from umit.core.I18N import _
from umit.core.Utils import amiroot
from umit.core.OptionsConf import options_file


class OptionTab(object):
    def __init__(self, root_tab, options, constructor, update_func):
        actions = {
                'option_list':self.__parse_option_list,
                'option_check':self.__parse_option_check}

        self.options = options
        self.constructor = constructor
        self.update_func = update_func
        self.widgets_list = []

        options_used = self.constructor.get_options()

        # Cannot use list comprehhension because text nodes raise exception
        # when tagName is called
        for option_element in root_tab.childNodes:
            try:option_element.tagName
            except:pass
            else:
                if option_element.tagName in actions:
                    self.widgets_list.append(
                            actions[option_element.tagName](option_element,
                                options_used))

    def __parse_option_list(self, option_list, options_used):
        options = option_list.getElementsByTagName(u'option')

        label = HIGEntryLabel(option_list.getAttribute(u'label'))
        opt_list = OptionList()

        for opt in options:
            opt_list.append(self.options.get_option(opt.getAttribute(u'name')))

        for i, row in enumerate(opt_list.list):
            if row[0] in options_used:
                opt_list.set_active(i)

        return label, opt_list

    def _disable_option(self, need_root):
        """
        enable / disable option if non-root user.
        """
        return not amiroot() and need_root


    def __with_icon(self, hint):
        """
        Return true or false: if is a option with icon or without.
        """
        return hint!=""

    def __parse_option_check(self, option_check, options_used):
        option = option_check.getAttribute(u'option')
        arg_type = self.options.get_arg_type(option)
        label = option_check.getAttribute(u'label')
        opt_parse = self.options.get_option(option)
        opt_hint = self.options.get_hint(option)
        need_root = self.options.get_need_root(option)
        with_icon = self.__with_icon(opt_hint)
        if with_icon:
            check = OptionCheckIcon(label, opt_parse, opt_hint )

        else:
            check = OptionCheck(label, opt_parse)
        check.set_active(option in options_used)
        if self._disable_option(need_root):
            check.disable_widget()
        type_mapping = {
                "str": OptionEntry,
                "int": OptionIntSpin,
                "float": OptionFloatSpin,
                "level": OptionLevelSpin,
                "path": OptionFile,
                "interface": OptionInterface}

        additional = None
        if type_mapping.has_key(arg_type):
            value = options_used.get(option, None)
            if value:
                additional = type_mapping[arg_type](value)
            else:
                additional = type_mapping[arg_type]()
        check.connect('toggled', self.update_check, additional)

        return check, additional

    def fill_table(self, table, expand_fill = True):
        yopt = (0, gtk.EXPAND | gtk.FILL)[expand_fill]
        for y, widget in enumerate(self.widgets_list):
            if widget[1] == None:
                table.attach(widget[0], 0, 2, y, y+1, yoptions=yopt)
            else:
                table.attach(widget[0], 0, 1, y, y+1, yoptions=yopt)
                table.attach(widget[1], 1, 2, y, y+1, yoptions=yopt)

        for widget in self.widgets_list:
            if isinstance(widget[1], OptionList):
                widget[1].connect('changed',self.update_list_option)
            elif isinstance(widget[1], OptionIntSpin) or\
                 isinstance(widget[1], OptionFloatSpin) or\
                 isinstance(widget[1], OptionEntry):
                widget[1].connect('changed', self.update_entry, widget[0])
            elif isinstance(widget[1], OptionLevelSpin):
                widget[1].connect('changed', self.update_level, widget[0])
            elif isinstance(widget[1], OptionFile):
                widget[1].entry.connect('changed', self.update_entry, widget[0])
            elif isinstance(widget[1], OptionInterface):
                widget[1].child.connect('changed', self.update_entry, widget[0])

    def update_check(self, check, extra):
        if check.get_active():
            if isinstance(extra, OptionEntry) or\
               isinstance(extra, OptionIntSpin) or\
               isinstance(extra, OptionFloatSpin):
                self.update_entry(extra, check)
            elif isinstance(extra, OptionLevelSpin):
                self.update_level(extra, check)
            elif isinstance(extra, OptionFile):
                self.update_entry(extra.entry, check)
            elif isinstance(extra, OptionInterface):
                self.update_entry(extra.child, check)
            else:
                self.constructor.add_option(check.option['name'])
        else:
            self.constructor.remove_option(check.option['name'])

        self.update_command()

    def update_entry(self, widget, check):
        if not check.get_active():
            check.set_active(True)

        self.constructor.remove_option(check.option['name'])
        self.constructor.add_option(check.option['name'], widget.get_text())

        self.update_command()

    def update_level(self, widget, check):
        if not check.get_active():
            check.set_active(True)

        try:
            self.constructor.remove_option(check.option['name'])
            if int(widget.get_text()) == 0:
                check.set_active(False)
            else:
                self.constructor.add_option(
                        check.option['name'],
                        level=int(widget.get_text()))
        except:pass

        self.update_command()

    def update_list_option(self, widget):
        try:widget.last_selected
        except:pass
        else:
            self.constructor.remove_option(widget.last_selected)

        option_name = widget.options[widget.get_active()]['name']

        self.constructor.add_option(option_name)
        widget.last_selected = option_name

        self.update_command()

    def update_command(self):
        if self.update_func:
            self.update_func()


class OptionBuilder(object):
    def __init__(self, xml_file, constructor, update_func):
        """ OptionBuilder(xml_file, constructor)

        xml_file is a UI description xml-file
        constructor is a CommandConstructor instance
        """
        xml_desc = open(xml_file)
        self.xml = minidom.parse(xml_desc)
        # Closing file to avoid problems with file descriptors
        xml_desc.close()

        self.constructor = constructor
        self.update_func = update_func

        self.root_tag = "interface"

        self.xml = self.xml.getElementsByTagName(self.root_tag)[0]
        self.options = NmapOptions(options_file)

        self.groups = self.__parse_groups()
        self.section_names = self.__parse_section_names()
        self.tabs = self.__parse_tabs()


    def __parse_section_names(self):
        dic = {}
        for group in self.groups:
            grp = self.xml.getElementsByTagName(group)[0]
            dic[group] = grp.getAttribute(u'label')
        return dic

    def __parse_groups(self):
        return [g_name.getAttribute(u'name') for g_name in \
                  self.xml.getElementsByTagName(u'groups')[0].\
                  getElementsByTagName(u'group')]

    def __parse_tabs(self):
        dic = {}
        for tab_name in self.groups:
            dic[tab_name] = OptionTab(
                    self.xml.getElementsByTagName(tab_name)[0],
                    self.options,
                    self.constructor,
                    self.update_func)
        return dic


class OptionWidget:
    def enable_widget(self):
        self.set_sensitive(True)

    def disable_widget(self):
        self.set_sensitive(False)

class OptionInterface(gtk.ComboBoxEntry, OptionWidget):
    def __init__(self):
        self.list = gtk.ListStore(str)
        gtk.ComboBoxEntry.__init__(self, self.list)

        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

class OptionList(gtk.ComboBox, OptionWidget):
    def __init__(self):
        self.list = gtk.ListStore(str)
        gtk.ComboBox.__init__(self, self.list)

        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

        self.options = []

    def append(self, option):
        self.list.append([option[u'name']])
        self.options.append(option)

class OptionCheckIcon(HIGHBox, OptionWidget):
    def __init__(self, label=None, option=None, hint=None):

        HIGHBox.__init__(self)

        self.cbutton = OptionCheck(label,option)
        self.option = option
        self.hint = Hint(hint)
        self.pack_start(self.cbutton, False, False)
        self.pack_start(self.hint, False, False, 5)

    def connect(self, action, func, additional):
        """
        connect checkbox
        """
        self.cbutton.connect(action, func, additional)

    def set_active(self, value):
        """
        set enable or disable checkbox
        """
        self.cbutton.set_active(value)

    def get_active(self):
        return self.cbutton.get_active()

    def get_checkbox(self):
        """
        Returns checkbox
        example, to do connection
        """
        return self.cbutton

    def get_option(self):
        return self.cbutton.get_option()


class OptionCheck(gtk.CheckButton, OptionWidget):
    def __init__(self, label=None, option=None):
        gtk.CheckButton.__init__(self, label)

        self.option = option

    def get_option(self):
        return self.option


class OptionEntry(gtk.Entry, OptionWidget):
    def __init__(self, param = ""):
        gtk.Entry.__init__(self)
        self.set_text(param)

class OptionLevelSpin(gtk.SpinButton, OptionWidget):
    def __init__(self, initial=0):
        gtk.SpinButton.__init__(self,gtk.Adjustment(int(initial),0,10,1),0.0,0)

class OptionIntSpin(gtk.SpinButton, OptionWidget):
    def __init__(self, initial=1):
        gtk.SpinButton.__init__(self,
                                gtk.Adjustment(int(initial),0,10**100,1),
                                0.0,0)

class OptionFloatSpin(gtk.SpinButton, OptionWidget):
    def __init__(self, initial=1):
        gtk.SpinButton.__init__(self,
                                gtk.Adjustment(float(initial),0,10**100,1),
                                0.1,2)

class OptionFile(HIGHBox, OptionWidget, object):
    def __init__(self, param=""):
        HIGHBox.__init__(self)

        self.entry = OptionEntry()
        self.button = HIGButton(stock=gtk.STOCK_OPEN)

        self._pack_expand_fill(self.entry)
        self._pack_noexpand_nofill(self.button)

        self.entry.set_text(param)
        self.button.connect('clicked', self.open_dialog_cb)

    def open_dialog_cb(self, widget):
        dialog = AllFilesFileChooserDialog(_("Choose file"))
        if dialog.run() == gtk.RESPONSE_OK:
            self.entry.set_text(dialog.get_filename())
        dialog.destroy()

    def get_filename(self):
        return "\ ".join(self.entry.get_text().split(" "))

    def set_filename(self, filename):
        self.entry.set_text(" ".join(filename.split("\ ")))

    filename = property(get_filename, set_filename)
class Hint(gtk.EventBox, object):
    def __init__(self, hint):
        gtk.EventBox.__init__(self)
        self.hint = hint

        self.hint_image = gtk.Image()
        self.hint_image.set_from_stock(
                gtk.STOCK_DIALOG_INFO,
                gtk.ICON_SIZE_SMALL_TOOLBAR)

        self.add(self.hint_image)
        self.add_events(gtk.gdk.BUTTON_MOTION_MASK)
        self.connect("button-press-event", self.show_hint)


    def show_hint(self, widget, event=None):
        hint_window = HintWindow(self.hint)
        hint_window.show_all()


class HintWindow(gtk.Window):

    def __init__(self, hint):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_position(gtk.WIN_POS_MOUSE)
        bg_color = gtk.gdk.color_parse("#fbff99")

        self.modify_bg(gtk.STATE_NORMAL, bg_color)

        self.event = gtk.EventBox()
        self.event.modify_bg(gtk.STATE_NORMAL, bg_color)
        self.event.set_border_width(10)
        self.event.connect("button-press-event", self.close)
        self.hint_label = gtk.Label(hint)
        self.hint_label.set_use_markup(True)
        self.hint_label.set_line_wrap(True)

        self.event.add(self.hint_label)
        self.add(self.event)

    def close(self, widget, event=None):
        self.destroy()
