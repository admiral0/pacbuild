#!/usr/bin/env python
# 
# strawberry - Main client daemon
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

import sys
import xmlrpclib
import threading
import os, os.path

from sqlobject import *

import strawberryConfig

class Build(SQLObject):
	cherryId = IntCol()
	sourceFilename = StringCol()
	source = StringCol()

	def _set_source(self, value):
		if value is not None:
			self._SO_set_source(value.encode('base64').replace('\n',''))
		else:
			self._SO_set_source(None)
	def _get_source(self):
		if self._SO_get_source() == None:
			return None
		else:
			return self._SO_get_source().decode('base64')

class Waka(threading.Thread):
	def __init__(self, filename, fileData, buildDir, **other):
		threading.Thread.__init__(self, *other)
		self.buildDir = buildDir
		self.filename = filename
		self.sourcePkg = os.path.join(self.buildDir, self.filename)
		self.makeWakaConf()
		self.makeSourceFile(fileData)

	def makeSourceFile(self, fileData):
		file = open(self.sourcePkg, "wb")
		file.write(fileData)
		file.close()

	def makeWakaConf(self):
		if (not os.path.isdir(self.buildDir)):
			os.makedirs(self.buildDir)
		self.mkchrootPath = os.path.join(self.buildDir,"mkchroot.conf")
		conf = open(self.mkchrootPath, "w")
		conf.write('WAKA_ROOT_DIR="%s"\n'%self.buildDir)
		conf.write('WAKA_CHROOT_DIR="chroot/"\n')
		conf.write('QUIKINST_LOCATION="/usr/share/waka/quickinst"\n')
		conf.write('PACKAGE_MIRROR_CURRENT="ftp://ftp.archlinux.org/current/os/${CARCH}"\n')
		conf.write('PACKAGE_MIRROR_EXTRA="ftp://ftp.archlinux.org/extra/os/${CARCH}"\n')
		conf.write('DEFAULT_PKGDEST=${WAKA_ROOT_DIR}/\n')
		conf.write('DEFAULT_KERNEL=kernel26\n')
		conf.close()

	def run(self):
		os.system("/usr/bin/mkchroot -o %s %s"%(self.mkchrootPath, self.sourcePkg))
		# Do the post build stuff

def canBuild():
	return Build.select().count() < strawberryConfig.maxBuilds

def getNextBuild():
	server = xmlrpclib.ServerProxy(strawberryConfig.url)
	build = server.getNextBuild(strawberryConfig.user, strawberryConfig.password)
	if build is not None and build is not False:
		return Build(cherryId=build[0], sourceFilename=build[1], source=build[2].decode('base64'))
	return None

def _main(argv=None):
	if argv is None:
		argv = sys.argv

	Build.setConnection(strawberryConfig.database)
	Build.createTable(ifNotExists=True)

	# Start any builds that never actually finished last time
	for i in Build.select():
		waka = Waka(i.sourceFilename, i.source, os.path.join(strawberryConfig.buildDir, i.sourceFilename))
		waka.start()

	while True:
		if canBuild():
			build = getNextBuild()
			if build is not None:
				print "Got a new build: %s" % build.sourceFilename
				
				# This is where you'd set up waka
				waka = Waka(build.sourceFilename, build.source, os.path.join(strawberryConfig.buildDir, build.sourceFilename))
				waka.start()
			

if __name__ == "__main__":
	sys.exit(_main())