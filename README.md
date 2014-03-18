jelly
=====

`jelly` is a [wxPython] based application framework.

The core of `jelly` is based around a duck-typing infused plugin system, which
enables the whole `jelly` application to be loosely coupled.
An event system provides a common communication interface for the different 
application-parts.

Contents
--------

- *logger.py*:    Jelly utilities the [python logging facility][logging]. 
                  Every module assumes that a properly configured hierarchical 
	          logger is present.
	          This module provides a function to create such a logger without 
	          the need to know anything about the python logging facility.
- *plugin.py*:    Plugin System 
- *event.py*:     Event System
- *gui.py*:       Application Core Factory
- *menu.py*:      Menu Factory
- *view.py*:      View Factory
- *baseobjs.py*:  Utility module with basic objects
- *structure.py*: Utility module for simple struct-like object
- *shortcut.py*:  Mixin to provide shortcut access

How to use
----------

This is a rundown of the included *"example.py"* file.

The first thing do, is to initialize the logger.

	from logger import configureLogger
	configureLogger()
	
Since jelly is based on wxPython, you should import wx.
	
	import wx
	
Import the needed parts of Jelly.

	from gui import InterfaceBuilder
	from view import ViewBuilder

Create a new application by inheriting from the `InterfaceBuilder`.

	class JellySampleApp(InterfaceBuilder):

		def showGui(self):
			self.prepare(title="Jelly Example Application", size=(400,150))
			self.show()
			
Create views, in this case a simple TextCtrl with a button, that show the text 
as an information-dialog if the button is clicked.
			
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

Load your application and show the GUI.
			
	if __name__ == "__main__":
		sample = JellySampleApp()
		sample.showGui()
		
All done!


[wxPython]: http://wxpython.org/
[logging]: http://docs.python.org/2/library/logging.html

