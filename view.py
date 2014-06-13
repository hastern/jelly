#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jelly Views

Contains the View builder and a Menu for accessing all available views.

The `ViewBuilder` utilises the *Advanced User Interface* library or more 
specific, the `auiNotebook`. The term *Perspective* in the later refers to the 
arrangement of views inside the `auiNotebook`.

"""

import logging
# We are assuming, that there is an already configured logger present
logger = logging.getLogger(__name__)

import os.path

import wx
import wx.gizmos
import wx.lib.agw.aui as aui

# other jelly modules
from baseobjs import CoreWindowObject
from plugin import PluginMount
from shortcut import ShortcutBuilder
from menu import MenuBuilder
from event import SkipEvent, EventBase
		
class PerspectiveSaveEvent(EventBase):
	"""The current perspective gets saved."""
	__slots__ = ['fname']
	"""The filename is the only member of this structure."""

class PerspectiveLoadEvent(EventBase):
	"""A perspective is loaded."""
	__slots__ = ['fname']
	"""The filename is the only member of this structure."""
		
class PerspectiveViewSelectEvent(EventBase):
	"""Event for selecting a view from the menu."""
	__slots__ = ['index']
	"""The index of the selected item"""
	
class PerspectiveTabCloseEvent(EventBase): 
	"""A tab gets closed"""
	pass
		
class PerspectiveResetEvent(EventBase): 
	"""The perspective gets reset"""
	pass

class ViewMenu(MenuBuilder):
	"""Menubuild plugin, creates a menu item for loading and saving the 
	perspective.
	"""
	def build(self):
		"""Build the view menu."""
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
		
		self.windowHandle.Bind(wx.EVT_MENU, self.loadPerspective,  itemLoad)
		self.windowHandle.Bind(wx.EVT_MENU, self.savePerspective,  itemSave)
		self.windowHandle.Bind(wx.EVT_MENU, self.resetPerspective, itemReset)
		
		PerspectiveTabCloseEvent.addHandler(self.updateViewsMenu)
		
		return self._menu, "&View", MenuBuilder.WeightAny
		
	
	def updateViewsMenu(self):
		"""The view menu contains a list of all available
		views in the application.
		Currently this is only one giant list."""
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
	def loadPerspective(self, event = None):	
		"""Event dispatcher, relays the Menu-Event from wxPython into 
		the jelly event system, by dispatching a PerspectiveLoadEvent."""
		fname = self.coreRef.loadFileDialog("Load Perspective", [('Perspective','.perspective')])
		if fname == "":
			raise SkipEvent()
		return fname
			
	@PerspectiveSaveEvent.dispatcher
	def savePerspective(self, event = None):
		"""Event dispatcher, relays the Menu-Event from wxPython into 
		the jelly event system, by dispatching a PerspectiveSaveEvent."""
		fname = self.coreRef.saveFileDialog("Save Perspective", [('Perspective','.perspective')])
		if fname == "":
			raise SkipEvent()
		return fname
	
	@PerspectiveResetEvent.dispatcher
	def resetPerspective(self, event = None):
		"""Event dispatcher, relays the Menu-Event from wxPython into 
		the jelly event system, by dispatching a PerspectiveResetEvent."""
		return None
		
	@PerspectiveViewSelectEvent.dispatcher
	def selectView(self, ev=None):
		"""Event dispatcher, relays the Menu-Event from wxPython into 
		the jelly event system, by dispatching a PerspectiveResetEvent.
		
		@return: The index of the selected item
		"""
		for idx, itm in enumerate(self.menuWindows.GetMenuItems()):
			if itm.GetId() == ev.GetId():
				return idx
		return -1
		
class ViewBuilder(CoreWindowObject, ShortcutBuilder):	
	"""The Menubuilder mainly consists of a list of views, that get inserted 
	into an `auiNotebook`.
	
	As a plugin hook is automatically collects all view plugins, which are 
	loaded into the application.
	
	Every plugin MUST implement to methods:
	- `createView(self, parent)` for creating the view elements
	- `updateView(self)` for updating the view elements
	"""
	__metaclass__ = PluginMount
	Title = 'View'
	"""The title of the view, gets display as the caption of the 
	corresponding tab."""
	name = "BaseView"
	"""The name of the view, for selecting them by a meaningful name rather 
	the class name"""
	Closeable = True
	"""By default, every view is closeable"""
	
	def __init__(self, *args, **kwargs):
		"""Initialize the ViewBuilder as a CoreWindowObject.
		This acts as a default initializer for all plugins.
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		"""
		CoreWindowObject.__init__(self, *args, **kwargs)
		self._created = False
		
	
	def onInit(self):
		"""Initialization callback, getting called after the default 
		initializer (`CoreObject.__init__`) is done.
		
		If the hook gets initialized, it add itself as a handler for
		PerspectiveViewSelectEvent, to correctly focus the selected 
		view. It also creates a list for all instances of views.
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		"""
		if self.isMount():
			self.views = []
			PerspectiveViewSelectEvent.addHandler(self.showView, 'index')
	
	def createView(self, parent = None):
		"""Instantiate all plugins, create the auiNotebook and 
		insert the contents of all views into separate tabs of the 
		notebook.
		
		Add EventHandler for all Perspective related events.
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		"""
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
				 | aui.AUI_NB_CLOSE_ON_ALL_TABS
		)
		#self.tabs = wx.Notebook(self.windowHandle)
		for idx,view in enumerate(self.views):
			if view.Title != "":
				logger.info("Loading view '{}'".format(view.Title))
				content = self.packContent(self.tabs, view=view)
				self.tabs.AddPage(content, view.Title)
				self.tabs.SetCloseButton(idx, view.Closeable)
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
		"""Eventhandler for closing tabs.
		Relays the wx Event into the jelly event system.
		A tab in the auiNotebook (in other words: a view) can enforce 
		not to be closeable.
		The normal behavior gets overridden.
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		
		@param event: the EVT_AUINOTEBOOK_PAGE_CLOSE event.
		"""
		assert self.isMount()
		tabIdx = self.tabs.GetSelection()
		if self.selectViewByIndex(tabIdx).Closeable:
			logger.debug("Closing tab[{}] '{}'".format(tabIdx, self.tabs.GetPageText(tabIdx)))
			self.tabs.DeletePage(tabIdx)
		else:
			logger.debug("Can't close tab[{}] '{}'".format(tabIdx, self.tabs.GetPageText(tabIdx)))
		event.Veto()
		
	def updateView(self):
		"""If called from the hook update all views.
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		"""
		if self.isMount():
			for view in self.views:
				if view._created:
					view.updateView()
					
	def loadPerspective(self, fname):
		"""Eventhandler for PerspectiveLoadEvent
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		
		@type  fname: str
		@param fname: Filename of the perspective
		"""
		assert self.isMount()
		logger.info("Loading perspective {}".format(fname))
		state = open(fname, "rb").read()
		self.tabs.LoadPerspective(state)
		
	def savePerspective(self, fname):
		"""Eventhandler for PerspectiveSaveEvent
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		
		@type  fname: str
		@param fname: Filename of the perspective
		"""
		assert self.isMount()
		logger.info("Saving perspective {}".format(fname))
		state = self.tabs.SavePerspective()
		open(fname, "wb").write(state)
		
	def resetPerspective(self):
		"""Eventhandler for PerspectiveResetEvent
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		"""
		assert self.isMount()
		logger.info("Reseting perspective")
		self.tabs.UnSplit()
			
	def selectView(self, name):
		"""Returns a view via access through its meaningful name
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		
		@type  name: str
		@param name: the meaningful name
		
		@raise KeyError: If the view does not exists
		
		@rtype:  ViewBuilder
		@return: The view
		"""
		assert self.isMount()
		for view in self.views:
			if view.name == name:
				return view
		raise KeyError("There is no view '{}'".format(name))
		
	def selectViewByIndex(self, index):
		"""Select a view by its index in the list.
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		
		@type  index: int
		@param index: Index of the view
		"""
		assert self.isMount()
		assert index >= 0
		assert index < len(self.views)
		return self.views[index]
		
	def isViewVisisble(self, view):
		"""Test if the view is visible, by checking if a tab with the
		title of the view exists in the auiNotebook.
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		
		@type  view: ViewBuilder
		@param view: The view
		
		@rtype:  Boolean
		"""
		assert self.isMount()
		for idx in xrange(self.tabs.GetPageCount()):
			lbl = self.tabs.GetPageText(idx)
			if lbl == view.Title:
				return True
		return False
		
	def showView(self, index):
		"""Eventhandler for PerspectiveViewSelectEvent
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		
		@type  index: int
		@param index: The view to be focused
		"""
		assert self.isMount()
		logger.debug("Showing page {}".format(index))
		view = self.selectViewByIndex(index)
		if not self.isViewVisisble(view):
			if view.Title != "":
				content = self.packContent(self.tabs, view=view)
				self.tabs.InsertPage(index, content, view.Title)
		self.tabs.SetSelection(index)
			
	def packContent(self, parent, name = None, view = None):
		"""Packs all elements of a view into a panel.
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		
		@type  parent: wx.Window
		@param parent: The parent of the panel
		
		@type  name: str
		@param name: The name of the view to be packed.
		             Only used when no view is given.
		
		@type  view: ViewBuilder
		@param view: The view to be packed.
		
		@rtype:  wx.Panel
		@return: The panel in which the elements got packed.
		"""
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
		"""Displays a view as a separate window.
		
		@type  self: ViewBuilder
		@param self: The ViewBuilder instance
		
		@type  name: str
		@param name: The name of the view to be packed.
		             Only used when no view is given.
		
		@type  view: ViewBuilder
		@param view: The view to be packed.
		
		@rtype:  wx.Frame
		@return: The Frame of the view.
		"""
		assert self.isMount()
		frame = wx.Frame(self.windowHandle)
		content = self.packContent(frame, name, view)
		return frame
		
	def defaultPanel(self, parent):
		"""Initializes the view with a simple panel.
		Will also creates a GridBagSizer.
		
		Panel and Sizer will be saved as "pnl" and "sizer" into the 
		class instance.
		
		@type  parent: wx.Window
		@param parent: The parent window
		"""
		self.pnl   = wx.Panel(parent)
		self.sizer = wx.GridBagSizer()
		self.pnl.SetSizer(self.sizer)
		
		return self.pnl, self.sizer

		
	def defaultScrollPanel(self, parent):
		"""Initializes the view with a panel, that has a scrollbar
		Will also creates a GridBagSizer.
		
		Panel and Sizer will be saved as "pnl" and "sizer" into the 
		class instance.
		
		@type  parent: wx.Window
		@param parent: The parent window
		"""
		self.pnl   = wx.ScrolledWindow(parent, style=wx.VSCROLL)
		self.sizer = wx.GridBagSizer()
		self.pnl.EnableScrolling(True, True)
		self.pnl.SetScrollRate(1,1)
		self.pnl.SetSizer(self.sizer)
		
		return self.pnl, self.sizer

	def defaultTree(self, parent, headers = [(),()], style = wx.SIMPLE_BORDER|wx.TR_HAS_BUTTONS|wx.TR_SINGLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_HIDE_ROOT):
		"""Initializes the view with a single TreeView
		
		@type  parent: wx.Window
		@param parent: The parent window
		
		@type  headers: list of tuple
		@param headers: A list of column headers and column widths
		
		@type  style: int
		@param style: The style of the Tree. Default: 
		              wx.SIMPLE_BORDER         |
			      wx.TR_HAS_BUTTONS        |
			      wx.TR_SINGLE             |
			      wx.TR_FULL_ROW_HIGHLIGHT | 
			      wx.TR_HIDE_ROOT
		
		"""
		self.tree = wx.gizmos.TreeListCtrl(parent, id=wx.ID_ANY, style=wx.SIMPLE_BORDER|wx.TR_HAS_BUTTONS|wx.TR_SINGLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_HIDE_ROOT)
		for header,width in headers:
			self.tree.AddColumn(text=header, width=width)
		return self.tree
		
	def defaultField(self, field, event, label, action= None, ctrlopts=dict(), sizeropts=dict(position = (0,0), span=(1,1), border=3, flags=wx.TOP|wx.EXPAND)):
		"""Create and place a new component.
		
		@type  field: wx.Window
		@param field: The type of the component
		
		@type  event: wx.Event
		@param event: The event to which the action will be bound
		
		@type  label: str
		@param label: The label for the component
		
		@type  action: Function or Bound Method
		@param action: The handler for the event 
		
		@type  ctrlopts: dict
		@param ctrlopts: The arguments passed to the constructor of the 
		                 component
				 
		@type  sizeropts: dict
		@param sizeropts: The options passed to the sizer call
		"""
		assert hasattr(self, "pnl")
		assert hasattr(self, "sizer")
		assert isinstance(self.sizer, wx.GridBagSizer)
		
		label = wx.StaticText(self.pnl, label=label)
		ctrl  = field(self.pnl, **ctrlopts)
		if action is not None:
			ctrl.Bind(event, action)
		
		self.sizer.Add(label, pos=sizeropts['position'], span=(1,1),  border=sizeropts['border'], flag=sizeropts['flags'])
		self.sizer.Add(ctrl, pos=(sizeropts['position'][0],sizeropts['position'][1]+1), span=sizeropts['span'], border=sizeropts['border'], flag=sizeropts['flags'])
		
		return ctrl
		
	def radioField(self, label, choices=list(), position = (0,0), span=(1,2), border=3, sizerFlags=wx.TOP|wx.EXPAND, action = None, style=0):
		"""Create and place a new component.
		
		@type  field: wx.Window
		@param field: The type of the component
		
		@type  event: wx.Event
		@param event: The event to which the action will be bound
		
		@type  label: str
		@param label: The label for the component
		
		@type  action: Function or Bound Method
		@param action: The handler for the event 
		
		@type  ctrlopts: dict
		@param ctrlopts: The arguments passed to the constructor of the 
		                 component
				 
		@type  sizeropts: dict
		@param sizeropts: The options passed to the sizer call
		"""
		assert hasattr(self, "pnl")
		assert hasattr(self, "sizer")
		assert isinstance(self.sizer, wx.GridBagSizer)
		
		ctrl  = wx.RadioBox(self.pnl, label=label, choices=choices, majorDimension=1)
		if action is not None:
			ctrl.Bind(event, action)
		ctrl.GetValue = ctrl.GetSelection
		ctrl.SetValue = ctrl.SetSelection
		
		self.sizer.Add(ctrl, pos=position, span=span, border=border, flag=sizerFlags)
		
		return ctrl	
		
	def buttonField(self, label="", caption=(), position = (0,0), span=(1,1), border=3, sizerFlags=wx.TOP|wx.EXPAND, action = None, style=0):
		"""Create a new text field (TextCtrl)
		Wraps the defaultField() Method
		
		@type  label: str
		@param label: The label of the field
		
		@type  caption: str
		@param caption: The caption of the button
		
		@type  position: tuple
		@param position: The position of the field inside the sizer
		
		@type  span: tuple
		@param span: The spanning of the field in the sizer
		
		@type  border: int
		@param border: The border between the components
		
		@type  sizerFlags: int 
		@param sizerFlags: The flags passed to the sizer.Add call
		
		@type  action: Function or Bound Method
		@param action: The event handler for the KILL_FOCUS event
		
		@type  style: int
		@param style: The style of the TextCtrl
		"""
		return self.defaultField(wx.Button, wx.EVT_BUTTON, label, action, ctrlopts=dict(style=style, value=value), sizeropts=dict(position=position, span=span, border=border, flags=sizerFlags))
	
	def textField(self, label="", value = "", position = (0,0), span=(1,1), border=3, sizerFlags=wx.TOP|wx.EXPAND, action = None, style=0):
		"""Create a new text field (TextCtrl)
		Wraps the defaultField() Method
		
		@type  label: str
		@param label: The label of the field
		
		@type  value: str
		@param value: The initial value for the field
		
		@type  position: tuple
		@param position: The position of the field inside the sizer
		
		@type  span: tuple
		@param span: The spanning of the field in the sizer
		
		@type  border: int
		@param border: The border between the components
		
		@type  sizerFlags: int 
		@param sizerFlags: The flags passed to the sizer.Add call
		
		@type  action: Function or Bound Method
		@param action: The event handler for the KILL_FOCUS event
		
		@type  style: int
		@param style: The style of the TextCtrl
		"""
		return self.defaultField(wx.TextCtrl, wx.EVT_KILL_FOCUS, label, action, ctrlopts=dict(style=style, value=value), sizeropts=dict(position=position, span=span, border=border, flags=sizerFlags))
		
	def numberField(self, label="", value = 0, min=0, max=100, position = (0,0), span=(1,1), border=3, sizerFlags=wx.TOP|wx.EXPAND, action = None, style=0):
		"""Create a new number field (SpinCtrl)
		Wraps the defaultField() Method
		
		@type  label: str
		@param label: The label of the field
		
		@type  value: int
		@param value: The initial value for the field
		
		@type  min: int
		@param min: The minimal value for the field
		
		@type  max: int
		@param max: The maximal value for the field
		
		@type  position: tuple
		@param position: The position of the field inside the sizer
		
		@type  span: tuple
		@param span: The spanning of the field in the sizer
		
		@type  border: int
		@param border: The border between the components
		
		@type  sizerFlags: int 
		@param sizerFlags: The flags passed to the sizer.Add call
		
		@type  action: Function or Bound Method
		@param action: The event handler for the KILL_FOCUS event
		
		@type  style: int
		@param style: The style of the TextCtrl
		"""
		return self.defaultField(wx.SpinCtrl, wx.EVT_SPINCTRL, label, action, ctrlopts=dict(style=style, initial=value, min=min, max=max), sizeropts=dict(position=position, span=span, border=border, flags=sizerFlags))
		
	def sliderField(self, label="", value = 0, min=0, max=100, position = (0,0), span=(1,1), border=3, sizerFlags=wx.TOP|wx.EXPAND, action = None, style=wx.SL_MIN_MAX_LABELS|wx.SL_AUTOTICKS):
		"""Create a new number field (Slider)
		Wraps the defaultField() Method
		
		@type  label: str
		@param label: The label of the field
		
		@type  value: int
		@param value: The initial value for the field
		
		@type  min: int
		@param min: The minimal value for the field
		
		@type  max: int
		@param max: The maximal value for the field
		
		@type  position: tuple
		@param position: The position of the field inside the sizer
		
		@type  span: tuple
		@param span: The spanning of the field in the sizer
		
		@type  border: int
		@param border: The border between the components
		
		@type  sizerFlags: int 
		@param sizerFlags: The flags passed to the sizer.Add call
		
		@type  action: Function or Bound Method
		@param action: The event handler for the KILL_FOCUS event
		
		@type  style: int
		@param style: The style of the TextCtrl (Default: wx.SL_MIN_MAX_LABELS|wx.SL_AUTOTICKS)
		"""
		return self.defaultField(wx.Slider, wx.EVT_SCROLL, label, action, ctrlopts=dict(style=style, value=value, minValue=min, maxValue=max), sizeropts=dict(position=position, span=span, border=border, flags=sizerFlags))
	
	def choiceField(self, label="", choices=(), selection="", position = (0,0), span=(1,1), border=3, sizerFlags=wx.TOP|wx.EXPAND, action = None, style=0):
		"""Create a new selection field (ComboBox)
		Wraps the defaultField() Method
		
		@type  label: str
		@param label: The label of the field
		
		@type  selection: str
		@param selection: The initial value for the field
		
		@type  choices: list
		@param choices: The choices for the selection
		
		@type  position: tuple
		@param position: The position of the field inside the sizer
		
		@type  span: tuple
		@param span: The spanning of the field in the sizer
		
		@type  border: int
		@param border: The border between the components
		
		@type  sizerFlags: int 
		@param sizerFlags: The flags passed to the sizer.Add call
		
		@type  action: Function or Bound Method
		@param action: The event handler for the KILL_FOCUS event
		
		@type  style: int
		@param style: The style of the TextCtrl (Default: wx.SL_MIN_MAX_LABELS|wx.SL_AUTOTICKS)
		"""
		return self.defaultField(wx.ComboBox, wx.EVT_COMBOBOX, label, action, ctrlopts=dict(style=style, value=selection, choices=map(str, choices)), sizeropts=dict(position=position, span=span, border=border, flags=sizerFlags))

		
		