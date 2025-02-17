#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
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

import unittest

class TestCase(unittest.TestCase):
	def testIfAllTestsAreEnabled(self):
		enabledTests = set(self._mm.mods("active", type="test"))
		allTests = set(self._mm.mods(type="test"))

		disabledTests = allTests - enabledTests
		self.assertEqual(disabledTests, set([]), msg=self._buildMessage(disabledTests))

	def _buildMessage(self, disabledTests):
		testPaths = (test.__class__.__file__ for test in disabledTests)
		joinedPaths = "\n".join(sorted(testPaths))
		return "These tests exist but are not run:\n" + joinedPaths

class TestModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "test"

	def enable(self):
		self.TestCase = TestCase
		self.TestCase._mm = self._mm
		self.active = True

	def disable(self):
		self.active = False
		del self.TestCase

def init(moduleManager):
	return TestModule(moduleManager)
