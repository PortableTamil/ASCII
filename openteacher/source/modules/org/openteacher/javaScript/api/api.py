#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012-2013, Marten de Vries
#
#	This file is part of OpenTeacher.
#
#	OpenTeacher is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	OpenTeacher is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.

class JavascriptApiModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(JavascriptApiModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "javaScriptApi"

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		with open(self._mm.resourcePath("api.js")) as f:
			self.code = f.read()

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.code

def init(moduleManager):
	return JavascriptApiModule(moduleManager)
