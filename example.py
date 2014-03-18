#/!usr/bin/env python
# -*- coding:utf-8 -*-


# Logger should be imported first
from logger import configureLogger
# Use default logger configuration
configureLogger()

# Import wx since this is what jelly is based around
import wx

# Import the needed parts of jelly
from gui import InterfaceBuilder
from view import ViewBuilder


class JellySampleApp(InterfaceBuilder):

	def showGui(self):
		self.prepare(title="Jelly Example Application", size=(400,150))
		self.show()
		
class JellySampleView(ViewBuilder):
	
	def createView(self, parent):
		panel = wx.Panel(parent)
		sizer = wx.BoxSizer()
		
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

