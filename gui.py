#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jelly Application Core


"""


import logging
# We are assuming, that there is an already configured logger present
logger = logging.getLogger(__name__)

import wx
import os.path
import itertools

# other jelly modules
from plugin import MixinMount
from menu import MenuBuilder
from view import ViewBuilder
from shortcut import ShortcutBuilder


class InterfaceBuilder(wx.App):
    """Jelly Interface Builder

    The interface builder is the application's core.
    It inherits from `wx.App` and behaves as one.

    The interface builder houses a `MenuBuilder` and `ViewBuilder` which form
    the interface. It will automatically load all available views and menus
    (meaning: in any loaded module).
    """
    __metaclass__ = MixinMount

    def __init__(self, *args, **kwargs):
        """

        @type  self: InterfaceBuilder
        @param self: The class instance
        """
        logger.debug("Initialize interface builder")
        self.helpProvider = wx.SimpleHelpProvider()
        wx.HelpProvider_Set(self.helpProvider)
        logger.info("Starting wxPython")
        wx.App.__init__(self, redirect=False)

        self.shortcuts = [
            (wx.ACCEL_NORMAL, wx.WXK_F5, self.update),
        ]
        self.shortcutIds = [
            (wx.ACCEL_CTRL, ord('q'), wx.ID_CLOSE),
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CLOSE),
        ]

    def prepare(self, title="Jelly Application", size=(1200, 700)):
        """Prepare the window, by loading all views and menu-entires.

        @type  self: InterfaceBuilder
        @param self: The class instance

        @type  title: str
        @param title: The title of the window

        @type  size: tuple
        @param size: The default size of the window
        """
        self.wHnd = wx.Frame(None, wx.NewId(), title, size=size, style=wx.DEFAULT_FRAME_STYLE)
        self.onWHndCreate()

        self.menu = MenuBuilder(self.wHnd, self)
        self.view = ViewBuilder(self.wHnd, self)
        self.view.createView()
        self.wHnd.SetMenuBar(self.menu.build())
        self.statusbar = self.wHnd.CreateStatusBar()

        self.wHnd.Bind(wx.EVT_MENU, self.OnCloseWindow, id=wx.ID_CLOSE)
        self.wHnd.Bind(wx.EVT_SIZE, self.update)
        self.wHnd.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        entries = []
        entries.extend(self.shortcutIds)
        entries.extend(self.view.getShortcutIds())
        entries.extend(self.menu.getShortcutIds())
        specialMapping = {wx.ACCEL_CTRL: "CTRL + ", wx.ACCEL_SHIFT: "Shift + ", wx.ACCEL_NORMAL: ""}
        keyMapping = {id: "F{}".format(i) for id, i in zip([wx.WXK_F1, wx.WXK_F2, wx.WXK_F3, wx.WXK_F4, wx.WXK_F5, wx.WXK_F6, wx.WXK_F7, wx.WXK_F8, wx.WXK_F9, wx.WXK_F10, wx.WXK_F11, wx.WXK_F12], itertools.count(1))}
        for special, key, func in itertools.chain(self.shortcuts, self.view.getShortcuts(), self.menu.getShortcuts()):
            logger.debug("Registering Shortcut {}{} to method {}".format(specialMapping[special], keyMapping[key] if key in keyMapping else chr(key), func))
            id = wx.NewId()
            entries.append((special, key, id))
            self.wHnd.Bind(wx.EVT_MENU, func, id=id)
        self.acceleratorTable = wx.AcceleratorTable(entries)
        self.wHnd.SetAcceleratorTable(self.acceleratorTable)

        self.SetTopWindow(self.wHnd)

        self.onPrepare()

        return self.wHnd

    def onWHndCreate(self):
        pass

    def onPrepare(self):
        pass

    def update(self, event=None):
        """Eventhandler for resize events.
        Updates all views.

        @type  self: InterfaceBuilder
        @param self: The class instance
        """
        self.view.updateView()
        if event is not None:
            event.Skip()

    def OnCloseWindow(self, e):
        """Eventhandler for the close event.
        Prompts the user if this was intentional.

        @type  self: InterfaceBuilder
        @param self: The class instance
        """
        ret = self.displayQuestion('Are you sure to quit?')
        if ret == wx.ID_YES:
            self.wHnd.Destroy()
            self.ExitMainLoop()

    def fileDialog(self, mode, message, fileTypes=None, dir=wx.EmptyString):
        """Displays a file dialog to open or save a file.

        @type  self: InterfaceBuilder
        @param self: The class instance

        @param mode: The mode of the dialog (save / open)

        @type  message: str
        @param message: The title of the dialog

        @param fileTypes: List of available filetypes

        @param dir: The default directory for the dialog
        """
        if fileTypes is None:
            wc = wx.FileSelectorDefaultWildcardStr
        else:
            wc = ""
            for descr, ext in fileTypes:
                wc += descr + " (*" + ext + ")|*" + ext + "|"
            wc = wc[:-1]  # remove trailing "|"

        diag = wx.FileDialog(self.wHnd, message, defaultDir=dir, wildcard=wc, style=mode)
        diag.ShowModal()
        return os.path.join(diag.Directory, diag.Filename) if diag.Filename != "" else ""

    def messageDialog(self, message, caption=wx.MessageBoxCaptionStr, style=wx.OK | wx.ICON_INFORMATION):
        """Displays a messagedialog.
        @type  self: InterfaceBuilder
        @param self: The class instance

        @type  message: str
        @param message: The message of the dialog

        @type  caption: str
        @param message: The cpation of the dialog

        @param style: The dialog style (Buttons & Icon)
        """
        dial = wx.MessageDialog(None, message, caption, style)
        return dial.ShowModal()

    def displayError(self, message, caption='An error occured'):
        """Displays an error message.

        @type  self: InterfaceBuilder
        @param self: The class instance

        @type  message: str
        @param message: The message of the dialog

        @type  caption: str
        @param message: The cpation of the dialog
        """
        return self.messageDialog(message, caption, wx.OK | wx.ICON_ERROR) == wx.OK

    def displayInformation(self, message, caption='Warning'):
        """Displays an information message.

        @type  self: InterfaceBuilder
        @param self: The class instance

        @type  message: str
        @param message: The message of the dialog

        @type  caption: str
        @param message: The cpation of the dialog
        """
        return self.messageDialog(message, caption, wx.OK | wx.ICON_INFORMATION) == wx.OK

    def displayQuestion(self, message, caption='Question'):
        """Displays a question.

        @type  self: InterfaceBuilder
        @param self: The class instance

        @type  message: str
        @param message: The message of the dialog

        @type  caption: str
        @param message: The cpation of the dialog
        """
        return self.messageDialog(message, caption, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

    def loadFileDialog(self, message="Load File", fileTypes=None, dir=wx.EmptyString):
        """File load dialog

        @type  self: InterfaceBuilder
        @param self: The class instance

        @type  message: str
        @param message: The title of the dialog

        @param fileTypes: List of available filetypes

        @param dir: The default directory for the dialog
        """
        return self.fileDialog(mode=wx.FD_OPEN, message=message, fileTypes=fileTypes, dir=dir)

    def saveFileDialog(self, message="Message", fileTypes=None, dir=wx.EmptyString):
        """File save dialog

        @type  self: InterfaceBuilder
        @param self: The class instance

        @type  message: str
        @param message: The title of the dialog

        @param fileTypes: List of available filetypes

        @param dir: The default directory for the dialog
        """
        return self.fileDialog(mode=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, message=message, fileTypes=fileTypes, dir=dir)

    def show(self):
        """Show the application window and start the event handling loop.

        @type  self: InterfaceBuilder
        @param self: The class instance
        """
        self.wHnd.Centre()
        self.wHnd.Show()
        self.MainLoop()
