#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
logger = logging.getLogger(__name__)

import wx

from baseobjs import CoreWindowObject
from plugin import PluginMount
from shortcut import ShortcutBuilder


class MenuBuilder(CoreWindowObject, ShortcutBuilder):
	__metaclass__ = PluginMount
	WeightAny = -1
		
	def preparePlugins(self):
		assert self.isMount()
		logger.info("Loading menu plugins")
		self.pluginInstances = MenuBuilder.loadPlugins(self.windowHandle, self.coreRef)
		self.registerShortcuts(self.pluginInstances)
		
	def build(self):
		assert self.isMount()
		self.preparePlugins()
		self._menu = wx.MenuBar()
		for plugin in self.pluginInstances:
			menu, title, weight = plugin.build()
			if weight != MenuBuilder.WeightAny:
				self._menu.Insert(weight, menu, title)
			else:
				self._menu.Append(menu, title)
		return self._menu
		
	def menu(self):
		return wx.Menu()
		
	def separator(self, menu):
		return menu.AppendSeparator()
		
	def item(self, menu, label = "Entry", hint = "", id=wx.ID_ANY, kind=wx.ITEM_NORMAL, image=""):
		item = wx.MenuItem(menu, id, label, hint, kind)
		item.SetBitmap(wx.ArtProvider.GetBitmap(image))
		menu.AppendItem(item)
		return item
		
	
	
	