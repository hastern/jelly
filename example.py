#/!usr/bin/env python
# -*- coding:utf-8 -*-


# Logger should be imported first
from logger import configureLogger
# Use default logger configuration
logger = configureLogger()

# Import wx since this is what jelly is based around
import wx

# Import the needed parts of jelly
from gui import InterfaceBuilder
from view import ViewBuilder
from menu import MenuBuilder


class JellySampleApp(InterfaceBuilder):

	def showGui(self):
		self.prepare(title="Jelly Example Application", size=(400,150))
		self.show()

class JellySampleMenu(MenuBuilder):
	def build(self):
		self._menu = self.menu()
		itemQuit = self.item(self._menu, label="&Quit", hint="Quit Example", id=wx.ID_EXIT, image=wx.ART_QUIT)
		self.windowHandle.Bind(wx.EVT_MENU, lambda e:self.windowHandle.Close(), itemQuit)
		return self._menu, "&File", 0

class JellySampleView(ViewBuilder):
	Title = "Example View"
	name = "example"
	def createView(self, parent):
		panel = wx.Panel(parent)
		sizer = wx.BoxSizer()
		print "Creating view"
		
		self.label  = wx.StaticText(panel, label="Input:")
		self.edit   = wx.TextCtrl(panel)
		self.button = wx.Button(panel, label="Click")
		
		sizer.Add(self.label, 0)
		sizer.Add(self.edit, 1)
		sizer.Add(self.button, 0)
		
		self.button.Bind(wx.EVT_BUTTON, self.OnClick)
		
		panel.SetSizer(sizer)
		return panel
		
	def OnClick(self, event):
		self.coreRef.displayInformation(self.edit.GetValue())
		self.edit.SetValue("")

if __name__ == "__main__":
	sample = JellySampleApp()
	sample.showGui()

