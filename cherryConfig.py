# 
# cherryConfig - Config file for cherry daemon
# Copyright (C) 2005 Jason Chu <jason@archlinux.org>
# 
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# 

from sqlobject import *
import os, os.path

arches = ['i586']

myHome = os.path.expanduser("~")

repos = [{'name':'current', 'absdir':'%s/pacbuild/abs'%myHome, 'repodir':'%s/pacbuild/repo'%myHome, 'updatescript':'/usr/bin/updatesync'}]

if not os.path.isdir("%s/.pacbuild"%myHome):
	os.makedirs("%s/.pacbuild"%myHome)
database = connectionForURI("sqlite://%s/.pacbuild/pacbuild.db"%myHome)
