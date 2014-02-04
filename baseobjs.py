#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

class CoreObject(object):
	def __init__(self, coreRef, *args, **kwargs):
		self.coreRef = coreRef
		if hasattr(self, "onInit"):
			self.onInit(*args, **kwargs)
		
class CoreWindowObject(CoreObject):
	def __init__(self, windowHandle, coreRef, *args, **kwargs):
		self.windowHandle = windowHandle
		CoreObject.__init__(self, coreRef, *args, **kwargs)