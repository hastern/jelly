#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jelly Basic Objects

Since the application is centered around its core, every
part of the application needs a direct reference to the core.
Through this reference it is possible to access almost any other part of
the application without knowing it directly.
"""

import logging
logger = logging.getLogger(__name__)


class CoreObject():
    """Core Object

    A core object knows a reference to its core.
    """
    def __init__(self, coreRef, *args, **kwargs):
        """
        @type  self: CoreObject
        @param self: The class instance

        @type  coreRef: InterfaceBuilder
        @param coreRef: The application core.
        """
        self.coreRef = coreRef
        if hasattr(self, "onInit"):
            self.onInit(*args, **kwargs)


class CoreWindowObject(CoreObject):
    """
    In addition to the CoreObject a CoreWindowObject also knows
    the windowHandle of the main window.
    """
    def __init__(self, windowHandle, coreRef, *args, **kwargs):
        """
        @type  self: CoreObject
        @param self: The class instance

        @type  windowHandle: wx.Frame
        @param windowHandle: The main window of the application

        @type  coreRef: InterfaceBuilder
        @param coreRef: The application core.
        """

        self.windowHandle = windowHandle
        CoreObject.__init__(self, coreRef, *args, **kwargs)
