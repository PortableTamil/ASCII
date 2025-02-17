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

CLIENT_ID = "5f1133e092b4eb1d610aecdb3a95e840"

import urllib2
import urllib
import json
import datetime
import logging

logger = logging.getLogger("flashcardexchange")

class FlashcardexchangeApi(object):
	"""See for documentation of the API this communicates with:
	   www.flashcardexchange.com/docs/api

	"""
	def __init__(self, appId, parse, getLanguageName, *args, **kwargs):
		super(FlashcardexchangeApi, self).__init__(*args, **kwargs)

		self._appId = appId
		self._parse = parse
		self._getLanguageName = getLanguageName

		self._baseUrl = "https://api.flashcardexchange.com/v2"

	def _open(self, url, **kwargs):
		kwargs["client_id"] = self._appId
		fullUrl = self._baseUrl + url + "?" + urllib.urlencode(kwargs)
		return urllib2.urlopen(fullUrl)

	def searchSets(self, searchTerm, page=1):
		try:
			fd = self._open("/search/sets", qstr=searchTerm, page=page)
		except urllib2.HTTPError, e:
			logger.debug(e)
			logger.debug(e.read())
			return {"results": []}
		return json.load(fd)

	def downloadSet(self, id):
		fd = self._open("/sets/%s" % id)
		data = json.load(fd)[0]

		created = datetime.datetime.strptime(data["created"], "%Y-%m-%d %H:%M:%S")

		list = {}
		list["title"] = data["title"]
		#maybe we need some fields for description & subject in our
		#file format...
		list["questionLanguage"] = self._getLanguageName(data["lang_front"])
		list["answerLanguage"] = self._getLanguageName(data["lang_back"])

		list["items"] = [
			{
				"id": card["card_id"],
				"created": created,
				"questions": self._parse(card["front"]),
				"answers": self._parse(card["back"]),
			}
			for card in data["cards"]
		]

		return {
			"list": list,
			"resources": {},
		}

def installQtClasses():
	global Model, SearchDialog

	class Model(QtCore.QAbstractListModel):
		def __init__(self, *args, **kwargs):
			super(Model, self).__init__(*args, **kwargs)

			self._choices = []

		def update(self, choices):
			"""Choices should be an iterable object of tuples of size two,
			   with in it first the text to display and second the value to
			   return by getChoice().

			"""
			self.beginResetModel()
			self._choices = choices
			self.endResetModel()

		def rowCount(self, parent):
			return len(self._choices)

		def data(self, index, role):
			if not (index.isValid() and role == QtCore.Qt.DisplayRole):
				return

			return self._choices[index.row()][0]

		def getChoice(self, index):
			return self._choices[index.row()][1]

	class SearchDialog(QtGui.QDialog):
		searchRequested = QtCore.pyqtSignal()

		def __init__(self, *args, **kwargs):
			super(SearchDialog, self).__init__(*args, **kwargs)

			self._label = QtGui.QLabel()
			self._label.setWordWrap(True)
			self._searchBox = QtGui.QLineEdit()
			self._searchButton = QtGui.QPushButton()
			self._searchButton.clicked.connect(self.searchRequested.emit)

			self._listView = QtGui.QListView()
			self._model = Model()
			self._listView.setModel(self._model)
			self._listView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
			self._listView.doubleClicked.connect(self.accept)

			buttonBox = QtGui.QDialogButtonBox(
				QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok,
				parent=self
			)
			buttonBox.accepted.connect(self.accept)
			buttonBox.rejected.connect(self.reject)

			hbox = QtGui.QHBoxLayout()
			hbox.addWidget(self._searchBox)
			hbox.addWidget(self._searchButton)

			l = QtGui.QVBoxLayout()
			l.addWidget(self._label)
			l.addLayout(hbox)
			l.addWidget(self._listView)
			l.addWidget(buttonBox)
			self.setLayout(l)

		@property
		def chosenResults(self):
			return [self._model.getChoice(i) for i in self._listView.selectedIndexes()]

		def setResults(self, results):
			self._model.update(results)

		@property
		def searchTerm(self):
			return unicode(self._searchBox.text())

		def retranslate(self):
			self._label.setText(_("Enter a search term and press the search button to search flashcardexchange.com for sets. Then select the set or sets you want to import and click OK."))
			self._searchBox.setPlaceholderText(_("E.g.: spanish travel vocabulary"))
			self._searchButton.setText(_("Search"))
			self.setWindowTitle(_("Search flashcardexchange.com"))

		def keyPressEvent(self, event):
			if event.key() != QtCore.Qt.Key_Return:
				#prevent the Ok button from triggering, most people
				#would expect it to be the search shortcut. (Which it
				#isn't, either.)
				return super(SearchDialog, self).keyPressEvent(event)

class FlashcardexchangeApiModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(FlashcardexchangeApiModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "flashcardexchangeApi"
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="buttonRegister"),
			self._mm.mods(type="wordsStringParser"),
			self._mm.mods(type="loaderGui"),
			self._mm.mods(type="languageCodeGuesser"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("flashcardexchangeApi.py",)

		self.priorities = {
			"default": 525,
		}

	@property
	def _getLanguageName(self):
		return self._modules.default("active", type="languageCodeGuesser").getLanguageName

	def enable(self):
		global QtCore, QtGui
		try:
			from PyQt4 import QtCore, QtGui
		except ImportError:
			return

		installQtClasses()

		self._modules = set(self._mm.mods(type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")
		self._buttonRegister = self._modules.default("active", type="buttonRegister")

		self._button = self._buttonRegister.registerButton("load-from-internet")
		self._button.clicked.handle(self.doImport)
		self._button.changePriority.send(self.priorities["default"])

		try:
			self._appIdSetting = self._modules.default(type="settings").registerSetting(**{
				"internal_name": "org.openteacher.flashcardexchangeApi.clientId",
				"type": "short_text",
				"defaultValue": CLIENT_ID,
				"advanced": True,
			})
		except IndexError:
			self._appIdSetting = {
				"value": CLIENT_ID,
			}

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	@property
	def _api(self):
		return FlashcardexchangeApi(self._appIdSetting["value"], self._parse, self._getLanguageName)

	def _retranslate(self):
		global _
		global ngettext

		#Install translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self._button.changeText.send(_("Import from flashcardexchange.com"))

		self._appIdSetting.update({
			"name": _("flashcardexchange.com API client id"),
		})

		#Translate all active dialogs
		if hasattr(self, "_dialog"):
			self._dialog.retranslate()
			self._dialog.tab.title = self._dialog.windowTitle()

	@property
	def _parse(self):
		return self._modules.default("active", type="wordsStringParser").parse

	def _handleSearch(self):
		try:
			data = self._api.searchSets(self._dialog.searchTerm)
		except urllib2.URLError, e:
			logger.debug(e, exc_info=True)
			self._noConnection()
			return
		self._dialog.setResults([
			(result["title"], result["set_id"])
			for result in data["results"]
		])

	def _noConnection(self):
		QtGui.QMessageBox.warning(
			self._uiModule.qtParent,
			_("No flashcardexchange.com connection"),
			_("flashcardexchange.com didn't accept the connection. Are you sure that your internet connection works and flashcardexchange.com is online?")
		)

	def doImport(self):
		try:
			self._dialog = SearchDialog()

			tab = self._uiModule.addCustomTab(self._dialog)
			tab.closeRequested.handle(tab.close)
			self._dialog.rejected.connect(tab.close)
			self._dialog.accepted.connect(tab.close)
			self._dialog.searchRequested.connect(self._handleSearch)
			self._dialog.tab = tab

			self._retranslate()
			self._dialog.accepted.connect(self._loadSelectedList)
		except urllib2.URLError, e:
			logger.debug(e, exc_info=True)
			self._noConnection()

	def _loadSelectedList(self):
		try:
			for setId in self._dialog.chosenResults:
				list = self._api.downloadSet(setId)
				try:
					self._loadList(list)
				except NotImplementedError:
					return
		except urllib2.URLError, e:
			logger.debug(e, exc_info=True)
			self._noConnection()
			return

		#everything went well
		self._uiModule.statusViewer.show(_("The word list was imported from flashcardexchange.com successfully."))

	def _loadList(self, list):
		self._modules.default("active", type="loaderGui").loadFromLesson("words", list)

	def disable(self):
		self.active = False

		self._buttonRegister.unregisterButton(self._button)

		del self._modules
		del self._uiModule
		del self._buttonRegister

		del self._button
		del self._appIdSetting

def init(moduleManager):
	return FlashcardexchangeApiModule(moduleManager)
