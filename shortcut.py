#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import wx

class ShortcutBuilder(object):
	
	def registerShortcuts(self, childs):
		self.sc_childs = childs
	
	def getShortcuts(self):
		if self.isMount():
			if self.sc_childs is not None:
				for child in self.sc_childs:
					for sc in child.getShortcuts():
						yield sc
				raise StopIteration()
		else:
			raise StopIteration()
			
	def getShortcutIds(self):
		if self.isMount():
			if self.sc_childs is not None:
				for child in self.sc_childs:
					for sc in child.getShortcutIds():
						yield sc
				raise StopIteration()
		else:
			raise StopIteration()

			