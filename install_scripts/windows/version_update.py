#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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

import os.path
import re
import os

from glob import glob

BASE_DIR = os.path.join("install_scripts", "windows")
VERSION_FILE = os.path.join("share", "umit", "config", "umit_version")

def umit_version():
    return open(VERSION_FILE).readlines()[0].split("\n")[0]

def umit_revision():
    stdin, stdout = os.popen2("svn info --xml")
    # I know that using regex to catch the revision in an XML may seem dull,
    # but it's the easier way to do that here
    return re.findall("revision=\"(\d+)\"", stdout.read())[0]

def get_winpcap():
    windeps = os.path.join(BASE_DIR, "win_dependencies", "winpcap*")
    return os.path.split(glob(windeps)[0])[1]

VERSION = umit_version()
REVISION = umit_revision()
WINPCAP = get_winpcap()
UMIT = "umit"

# List of files to update:
# install_scripts\windows\setup.py
# install_scripts\windows\umit_compiled.nsi
# umitCore\Paths.py

setup = os.path.join(BASE_DIR, "setup.py")
umit_compiled = os.path.join(BASE_DIR, "umit_compiled.nsi")
paths = os.path.join("umitCore", "Paths.py")

assert os.path.exists(setup)
assert os.path.exists(umit_compiled)
assert os.path.exists(paths)
assert os.path.exists(os.path.join(BASE_DIR, "win_dependencies", WINPCAP))

print "Updating some files with the current Umit version and revision..."
print "VERSION:", VERSION
print "REVISION:", REVISION
print "WINPCAP:", WINPCAP

print
print "Updating:", setup
sf = open(setup)
setup_content = sf.read()
sf.close()

setup_content = re.sub("VERSION\s+=\s+\"(\d+)\"",
                       "VERSION = \"%s\"" % VERSION,
                       setup_content)
setup_content = re.sub("REVISION\s+=\s+\"(\d+)\"",
                       "REVISION = \"%s\"" % REVISION,
                       setup_content)

sf = open(setup, "w")
sf.write(setup_content)
sf.close()


print "Updating:", umit_compiled
ucf = open(umit_compiled)
ucompiled_content = ucf.read()
ucf.close()

ucompiled_content = re.sub("!define APPLICATION_VERSION \".+\"",
                           "!define APPLICATION_VERSION \"%s\"" % VERSION,
                           ucompiled_content)
ucompiled_content = re.sub("!define WINPCAP \".+\"",
                           "!define WINPCAP \"%s\"" % WINPCAP,
                           ucompiled_content)

ucf = open(umit_compiled, "w")
ucf.write(ucompiled_content)
ucf.close()


print "Updating:", paths
pf = open(paths)
paths_content = pf.read()
pf.close()

paths_content = re.sub("VERSION\s+=\s+\"\d+\"",
                       "VERSION = \"%s\"" % VERSION,
                       paths_content)
paths_content = re.sub("REVISION\s+=\s+\"\d+\"",
                       "REVISION = \"%s\"" % REVISION,
                       paths_content)

pf = open(paths, "w")
pf.write(paths_content)
pf.close()

print "Setting umit to production..."
uf = open("umit")
umit_content = uf.read()
uf.close()

umit_content = re.sub("DEVELOPMENT\s+=\s+(True|False)",
                      "DEVELOPMENT = False",
                      umit_content)

uf = open("umit.pyw", "w")
uf.write(umit_content)
uf.close()

print "Updating:", VERSION_FILE
vf = open(VERSION_FILE, "w")
print [VERSION, REVISION]
vf.write("\n".join([VERSION, REVISION]))
vf.close()

print
print "Done!"