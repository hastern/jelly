#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jelly Menu


Currently only supports a single menu bar.
"""


import logging
# We are assuming, that there is an already configured logger present
logger = logging.getLogger(__name__)

import wx

# other jelly modules
from baseobjs import CoreWindowObject
from plugin import PluginMount
from shortcut import ShortcutBuilder


class MenuBuilder(CoreWindowObject, ShortcutBuilder):
    """The menu builder constructs the main menu of the application.

    Each plugin servers as a new item in the main menu bar.
    """
    __metaclass__ = PluginMount
    WeightAny = -1
    """Classmember describing the ordering of menu items"""

    def preparePlugins(self):
        """Load all available menus and register their shortcuts.

        @type  self: MenuBuilder
        @param self: Class Instance
        """
        assert self.isMount()
        logger.info("Loading menu plugins")
        self.pluginInstances = MenuBuilder.loadPlugins(self.windowHandle, self.coreRef)
        self.registerShortcuts(self.pluginInstances)

    def build(self):
        """Build the main menu by collecting all menu items from the
        plugins.

        @type  self: MenuBuilder
        @param self: Class Instance
        """
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

    def menu(self, parent=None, title="Menu"):
        """Creates a new menu (e.g. a collection of items)
        Encapsulate the behavior of wxPython for the plugins.

        @type  self: MenuBuilder
        @param self: Class Instance
        """
        menu = wx.Menu()
        if parent is not None:
            parent.AppendMenu(id=wx.NewId(), text=title, submenu=menu)
        return menu

    def separator(self, menu):
        """Appends a separator to a given menu
        Encapsulate the behavior of wxPython for the plugins.

        @type  self: MenuBuilder
        @param self: Class Instance

        @param menu: The menu
        """
        return menu.AppendSeparator()

    def item(self, menu, label="Entry", hint="", id=wx.ID_ANY, kind=wx.ITEM_NORMAL, image=None):
        """Appends a new item to a given menu
        Encapsulate the behavior of wxPython for the plugins.


        @type  self: MenuBuilder
        @param self: Class Instance

        @param menu: The menu

        @type  label: str
        @param label: The label / Text of the item

        @type  hint: str
        @param hint: The helptext of the item.
                     Gets display in the statusbar, while hovering.

        @type  id: int
        @param id: The ID of the item

        @type  kind: int
        @param kind: The kind of the item
                     (ITEM_NORMAL, ITEM_CHECK, ITEM_RADIO)

        @type  image: Bitmap
        @param image: The icon of the item
        """
        item = wx.MenuItem(parentMenu=menu, id=id, text=label, help=hint, kind=kind)
        if image is not None:
            item.SetBitmap(wx.ArtProvider.GetBitmap(image))
        menu.AppendItem(item)
        return item
