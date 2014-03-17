#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os.path

import wx
import wx.lib.agw.aui as aui

from baseobjs import CoreWindowObject
from plugin import PluginMount
from shortcut import ShortcutBuilder
from menu import MenuBuilder
from event import SkipEvent, EventBase
		
class PerspectiveSaveEvent(EventBase):
	__slots__ = ['fname']

class PerspectiveLoadEvent(EventBase):
	__slots__ = ['fname']
		
class PerspectiveShowEvent(EventBase):
	__slots__ = ['index']
	
class PerspectiveTabCloseEvent(EventBase): pass
		
class PerspectiveResetEvent(EventBase): pass

class ViewMenu(MenuBuilder):
	def build(self):
		self._menu = self.menu()
		self._idLoad = wx.NewId()
		self._idSave = wx.NewId()
		self._idReset = wx.NewId()
		itemLoad = self.item(self._menu, label="Load Perspective", hint="Open an existing Perspective", id=self._idLoad, image=wx.ART_FILE_OPEN)
		itemSave = self.item(self._menu, label="Save Perspective", hint="Save current Perspective", id=self._idSave, image=wx.ART_FILE_SAVE)
		self.separator(self._menu)
		itemReset = self.item(self._menu, label="Reset Perspective", hint="Reset Perspective to default", id=self._idReset, image=wx.ART_UNDO)
		
		self.menuWindows = self.menu(parent = self._menu, title = "Views")
		self.updateViewsMenu()
		
		self.windowHandle.Bind(wx.EVT_MENU, lambda e:self.loadPerspective(), itemLoad)
		self.windowHandle.Bind(wx.EVT_MENU, lambda e:self.savePerspective(), itemSave)
		self.windowHandle.Bind(wx.EVT_MENU, lambda e:self.resetPerspective(), itemReset)
		
		PerspectiveTabCloseEvent.addHandler(self.updateViewsMenu)
		
		return self._menu, "&View", MenuBuilder.WeightAny
		
	
	def updateViewsMenu(self):
		# Append lines
		while self.menuWindows.GetMenuItemCount() < len(self.coreRef.view.views):
			itm = self.item(self.menuWindows, label="()", hint="Show View", id=wx.NewId(), kind=wx.ITEM_CHECK)
			self.windowHandle.Bind(wx.EVT_MENU, self.selectView, itm)
		# Remove lines
		while self.menuWindows.GetMenuItemCount() > len(self.coreRef.view.views):
			itm = self.menuWindows.FindItemByPosition(0)
			self.windowHandle.Unbind(itm)
			self.menuWindows.Delete(itm.GetId())
		# Update labels
		for idx,view in enumerate(self.coreRef.view.views):
			itm = self.menuWindows.FindItemByPosition(idx)
			itm.SetItemLabel(view.Title)
			itm.SetHelp("Display '{}'".format(view.Title))
			if self.coreRef.view.isViewVisisble(view):
				itm.Check()
			else:
				itm.Check(False)
		
	@PerspectiveLoadEvent.dispatcher
	def loadPerspective(self):
		fname = self.coreRef.loadFileDialog("Load Perspective", [('Perspective','.perspective')])
		if fname == "":
			raise SkipEvent()
		return fname
			
	@PerspectiveSaveEvent.dispatcher
	def savePerspective(self):
		fname = self.coreRef.saveFileDialog("Save Perspective", [('Perspective','.perspective')])
		if fname == "":
			raise SkipEvent()
		return fname
	
	@PerspectiveResetEvent.dispatcher
	def resetPerspective(self):
		return None
		
	@PerspectiveShowEvent.dispatcher
	def selectView(self, ev=None):
		for idx, itm in enumerate(self.menuWindows.GetMenuItems()):
			if itm.GetId() == ev.GetId():
				return idx
		return -1
		
class ViewBuilder(CoreWindowObject, ShortcutBuilder):
	__metaclass__ = PluginMount
	Title = 'View'
	name = "BaseView"
	Closeable = True
	
	def __init__(self, *args, **kwargs):
		CoreWindowObject.__init__(self, *args, **kwargs)
		self._created = False
		
		if self.isMount():
			PerspectiveShowEvent.addHandler(self.showView, 'index')
	
	def onInit(self):
		if self.isMount():
			self.views = []
	
	def createView(self, parent = None):
		assert self.isMount()
		self.views = ViewBuilder.loadPlugins(self.windowHandle, self.coreRef)
					
		self.tabs = aui.AuiNotebook(self.windowHandle, id=wx.ID_ANY, 
			agwStyle = aui.AUI_NB_TOP 
			         | aui.AUI_NB_TAB_SPLIT 
				 | aui.AUI_NB_TAB_MOVE 
				 | aui.AUI_NB_SCROLL_BUTTONS 
				 | aui.AUI_NB_DRAW_DND_TAB 
				 | aui.AUI_NB_WINDOWLIST_BUTTON 
				 | aui.AUI_NB_TAB_FLOAT 
				 | aui.AUI_NB_TAB_EXTERNAL_MOVE
				 | aui.AUI_NB_CLOSE_BUTTON
		)
		#self.tabs = wx.Notebook(self.windowHandle)
		for view in self.views:
			if view.Title != "":
				content = self.packContent(self.tabs, view=view)
				self.tabs.AddPage(content, view.Title)
		self.registerShortcuts(self.views)
		
		self.tabs.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnCloseTab)
		#self.tabs.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.OnTabClosed)
		
		PerspectiveLoadEvent.addHandler(self.loadPerspective, 'fname')
		PerspectiveSaveEvent.addHandler(self.savePerspective, 'fname')
		PerspectiveResetEvent.addHandler(self.resetPerspective)
		
		if os.path.exists("default.perspective"):
			self.loadPerspective("default.perspective")
			
	@PerspectiveTabCloseEvent.dispatcher
	def OnCloseTab(self, event):
		assert self.isMount()
		tabIdx = self.tabs.GetSelection()
		if self.selectViewByIndex(tabIdx).Closeable:
			logger.debug("Closing tab[{}] '{}'".format(tabIdx, self.tabs.GetPageText(tabIdx)))
			self.tabs.DeletePage(tabIdx)
		else:
			logger.debug("Can't close tab[{}] '{}'".format(tabIdx, self.tabs.GetPageText(tabIdx)))
		event.Veto()
		
	def updateView(self):
		if self.isMount():
			for view in self.views:
				if view._created:
					view.updateView()
					
	def loadPerspective(self, fname):
		assert self.isMount()
		logger.info("Loading perspective {}".format(fname))
		state = open(fname, "rb").read()
		self.tabs.LoadPerspective(state)
		
	def savePerspective(self, fname):
		assert self.isMount()
		logger.info("Saving perspective {}".format(fname))
		state = self.tabs.SavePerspective()
		open(fname, "wb").write(state)
		
	def resetPerspective(self):
		assert self.isMount()
		logger.info("Reseting perspective")
		self.tabs.UnSplit()
			
	def selectView(self, name):
		assert self.isMount()
		for view in self.views:
			if view.name == name:
				return view
		raise KeyError("There is no view '{}'".format(name))
		
	def selectViewByIndex(self, index):
		assert self.isMount()
		assert index >= 0
		assert index < len(self.views)
		return self.views[index]
		
	def isViewVisisble(self, view):
		assert self.isMount()
		for idx in xrange(self.tabs.GetPageCount()):
			lbl = self.tabs.GetPageText(idx)
			if lbl == view.Title:
				return True
		return False
		
	def showView(self, index):
		assert self.isMount()
		logger.debug("Showing page {}".format(index))
		view = self.selectViewByIndex(index)
		if not self.isViewVisisble(view):
			if view.Title != "":
				content = self.packContent(self.tabs, view=view)
				self.tabs.InsertPage(index, content, view.Title)
		else:
			self.tabs.SetSelection(index)
			
	def packContent(self, parent, name = None, view = None):
		assert self.isMount()
		if view is None:
			view = self.selectView(name)
		pnl = wx.Panel(parent, id = wx.ID_ANY)
		sizer = wx.BoxSizer(wx.VERTICAL)
		page = view.createView(pnl)
		view._created = True
		sizer.Add(page, 1, wx.EXPAND|wx.ALL, 3)
		pnl.SetSizer(sizer)
		return pnl
			
	def showAsWindow(self, name = None, view = None):
		assert self.isMount()
		frame = wx.Frame(self.windowHandle)
		content = self.packContent(frame, name, view)
		return frame
		
	
