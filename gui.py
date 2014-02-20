#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import wx


from plugin import PluginMount
from menu import MenuBuilder
from view import ViewBuilder


class InterfaceBuilder(wx.App):
	__metaclass__ = PluginMount
	
	def __init__(self, *args, **kwargs):
		logger.debug("Initialise interface builder")
		logger.info("Starting wxPython")
		wx.App.__init__(self, redirect = False, useBestVisual=True)
	
	def prepare(self, title="Jelly Application", size=(1200,700)):
		logger.debug("loading interface plugins")
		self.preparePlugins()
		self.wHnd = wx.Frame(None, wx.NewId(), title, size=size, style=wx.DEFAULT_FRAME_STYLE)
		logger.debug("Loading Menu")
		
		self.menu = MenuBuilder(self.wHnd, self)
		self.view = ViewBuilder(self.wHnd, self)
		
		self.view.createView()
		self.wHnd.SetMenuBar(self.menu.build())
		self.statusbar = self.wHnd.CreateStatusBar()
		
		self.refreshId = wx.NewId()
		self.wHnd.Bind(wx.EVT_MENU, self.OnCloseWindow, id = wx.ID_CLOSE)
		self.wHnd.Bind(wx.EVT_SIZE, self.update)
		self.wHnd.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		self.wHnd.Bind(wx.EVT_MENU, self.update, id = self.refreshId)
		
		entries = []
		entries.extend(self.view.getShortcutIds())
		entries.extend(self.menu.getShortcutIds())
		entries.append((wx.ACCEL_CTRL,  ord('q'), wx.ID_CLOSE))
		entries.append((wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CLOSE))
		entries.append((wx.ACCEL_NORMAL,  wx.WXK_F5, self.refreshId))
		for special, key, func in self.view.getShortcuts():
			id = wx.NewId()
			entries.append((special,key,id))
			self.wHnd.Bind(wx.EVT_MENU, func, id = id)
		self.acceleratorTable = wx.AcceleratorTable(entries)
		self.wHnd.SetAcceleratorTable(self.acceleratorTable)	
		
		self.SetTopWindow(self.wHnd)
		
		return self.wHnd
		
	def preparePlugins(self):
		logger.info("Loading core plugins")
		self.plugins = InterfaceBuilder.loadPlugins(caller = self)
		logger.debug("Collecting plugin methods for {}".format(self.__class__))
		self.pluginMethods = {}
		for plug in self.plugins:
			logger.debug("\tPlugin: {}".format(plug.__class__))
			for k in plug.__dict__:
				e = plug.__dict__[k]
				if not (k.startswidth("__") or k.endswidth("__")) and hasattr(e, "__call__"):
					self.pluginMethods[k] = (plug, e)
					
	def __getattr__(self, attr):
		if attr in self.__dict__:
			return self.__dict__[attr]
		elif attr in self.pluginMethods:
			plugin, method = self.pluginMethods[attr]
			return plugin.method
		else:
			return super(wx.App, self).__getattr__(attr)
		
	def update(self, event = None):
		self.view.updateView()
		if event is not None:
			event.Skip()
			

	def OnCloseWindow(self, e):
		ret = self.displayQuestion('Are you sure to quit?')
		if ret == wx.ID_YES:
			self.wHnd.Destroy()
			self.ExitMainLoop()
			
	
	def fileDialog(self, mode, message, fileTypes = None, dir = wx.EmptyString):
		if fileTypes is None:
			wc = wx.FileSelectorDefaultWildcardStr
		else:
			wc = ""
			for descr, ext in fileTypes:
				wc += descr + " (*" +  ext + ")|*" + ext + "|"
			wc = wc[:-1] # remove trailing "|"
				
		diag = wx.FileDialog(self.wHnd, message, defaultDir=dir, wildcard = wc, style=mode)
		diag.ShowModal()
		return diag.Filename
	
	def messageDialog(self, message, caption=wx.MessageBoxCaptionStr, style=wx.OK | wx.ICON_INFORMATION):
		dial = wx.MessageDialog(None, message, caption, style)
		return dial.ShowModal()
		
	def displayError(self, message, caption = 'An error occured'):
		return self.messageDialog(message, caption, wx.OK | wx.ICON_ERROR) == wx.OK
		
	def displayInformation(self, message, caption='Warning'):
		return self.messageDialog(message, caption, wx.OK | wx.ICON_INFORMATION) == wx.OK
		
	def displayQuestion(self, message, caption='Question'):
		return self.messageDialog(message, caption, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		
	def loadFileDialog(self, message = "Load File", fileTypes = None, dir = wx.EmptyString):
		return self.fileDialog(mode = wx.FD_OPEN, message= message, fileTypes = fileTypes, dir = dir)
		
	def saveFileDialog(self, message = "Message", fileTypes = None, dir = wx.EmptyString):
		return self.fileDialog(mode = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, message= message, fileTypes = fileTypes, dir = dir)
		
	def show(self):
		self.wHnd.Centre()
		self.wHnd.Show()
		self.MainLoop()
		

