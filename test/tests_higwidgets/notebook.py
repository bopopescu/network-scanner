#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         Cleber Rodrigues <cleber.gnu@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import gtk
from HIGWidgets import *

def button_start_cb(w, p):
    p.start()
def button_stop_cb(w, p):
    p.stop()

win = gtk.Window()
win.connect('delete-event', gtk.main_quit)

def cb(data):
    print 'close-clicked'

n = HIGNotebook()

for i in range(6):
    t = HIGAnimatedTabLabel("Page %s" % i)
    t.connect('close-clicked', cb)
    n.append_page(gtk.Button("teste"), t )

win.add(n)
win.show_all()

gtk.main()
