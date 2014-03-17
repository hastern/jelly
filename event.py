#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from functools import wraps

from structure import Structure

class SkipEvent(Exception): pass

class Event(type):
	"""Event handling system."""
	def __init__(cls, name, bases, attrs):	
		"""Give every class-object its own handler list"""
		cls.handlers = []
		logger.debug("Creating handler list on {}".format(cls))

	def dispatcher(cls, func):
		"""Event dispatchter - Function decorator
		Take the result of the dispatcher function and wrap it into the
		corresponding event."""
		@wraps(func)
		def eventDispatcher(self, *args, **kwargs):
			try:
				ret = func(self, *args, **kwargs)
				if isinstance(ret, tuple) and hasattr(ret, "__len__"):
					params = ret
				else:
					params = (ret, )
				for handler in cls.handlers:
					handler(cls(*params))
			except SkipEvent:
				pass
		return eventDispatcher
	
	def fire(cls, *args, **kwargs):
		ev = cls(*args, **kwargs)
		
		for handler in cls.handlers:
			handler(ev)
		
	def addHandler(cls, handler, *args):
		logger.debug("Adding handler {}{} to '{}'".format(handler.__name__, args, cls.__class__.__name__,))
		@wraps(handler)
		def eventHandler(ev):
			params = []
			for arg in args:
				params.append(ev.__getattribute__(arg))
			return handler(*params)
		cls.handlers.append(eventHandler)
		
	def removeHandler(cls, handler):
		cls.handlers.remove(handler)
		
	def __iadd__(cls, handler):
		cls.addHandler(handler)
	def __isub__(cls, handler):
		cls.removeHandler(handler)
				
class EventBase(Structure):
	__metaclass__ = Event
	__slots__ = []

