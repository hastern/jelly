#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jelly Event - Event System

The event system works like the plugin system, by hooking handlers into the 
class-object.

Events get dispatched by method decoration.

Since handling the events is context-dependent, event handler can't be 
defined by method decoration.
"""


import logging
# We are assuming, that there is an already configured logger present
logger = logging.getLogger(__name__)

# Needed for function decorators
from functools import wraps
# Import jelly.structure
from structure import Structure

class SkipEvent(Exception): pass
"""Exception signal to not fire an event"""

class Event(type):
	"""Event handling system."""
	def __init__(cls, *args):	
		"""Give every class-object its own handler list"""
		cls.handlers = []
		logger.debug("Creating handler list on {}".format(cls.__name__))

	def dispatcher(cls, func):
		"""Event dispatcher - Function decorator
		Take the result of the dispatcher function and wrap it into the
		corresponding event.
		
		To not dispatch an event raise a `SkipEvent` Exception.
		
		@type  cls: object
		@param cls: The class-object of the event to be dispatched
		
		@type  func: method
		@param func: The dispatcher function.
		
		@rtype:  method
		@return: Decorated dispatcher function
		"""
		logger.debug("New {}.dispatcher: {}".format(cls.__name__, func))
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
		"""
		Adds handler to an Event.
		
		@type  cls: object
		@param cls: The class-object of the event to be dispatched
		
		@type  handler: method
		@param handler: The handler function
		
		@type  *args: list
		@param *args: A list of elements from the event passed to the 
		              handler
		"""
		logger.debug("Adding handler {}.{}{} to '{}'".format(handler.im_class.__name__,handler.__name__, args, cls.__name__,))
		@wraps(handler)
		def eventHandler(ev):
			params = []
			for arg in args:
				params.append(ev.__getattribute__(arg))
			return handler(*params)
		cls.handlers.append(eventHandler)
		
	def removeHandler(cls, handler):
		"""
		Removes a handler from an Event.
		
		@type  cls: object
		@param cls: The class-object of the event to be dispatched
		
		@type  handler: method
		@param handler: The handler function
		"""
		cls.handlers.remove(handler)
		
	def __iadd__(cls, handler):
		"""Operator overloading for addHandler"""
		cls.addHandler(handler)
	def __isub__(cls, handler):
		"""Operator overloading for removeHandler"""
		cls.removeHandler(handler)
				
class EventBase(Structure):
	"""Base Event, All events should Inherit from this one"""
	__metaclass__ = Event
	__slots__ = []

