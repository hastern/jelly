#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Jelly utilities the python logging facility.
Every module assumes that a properly configured hierarchical logger is present.
This module provides a function to create such a logger without the need to 
know anything about the python logging facility.
"""

import logging

from event import EventBase

class JellyLogEvent(EventBase):
	__slots__ = ['record', 'message']

class JellyEventLogHandler(logging.Handler):

	def __init__(self):
		logging.Handler.__init__(self)
		
	@JellyLogEvent.dispatcher
	def emit(self, record):
		s = self.format(record)
		return record, s


def configureLogger(name = "jelly", formatString = '%(asctime)s [%(levelname)s] %(name)s: %(message)s', level = logging.DEBUG):
	"""
	Configure a logger for the python logging facility.
	
	@type  name: str
	@param name: The name of the logger
	
	@type  formatString: string
	@param formatString: The format string for the logging output.
	
	@type  level: int
	@param level: The loglevel
	
	@return: the logger instance
	@rtype:  logging.Logger
	"""
	logger = logging.getLogger(name)
	streamHandler = logging.StreamHandler()
	jellyHandler  = JellyEventLogHandler()
	formatter = logging.Formatter(formatString)
	streamHandler.setFormatter(formatter)
	jellyHandler.setFormatter(formatter)
	logger.addHandler(streamHandler)
	logger.addHandler(jellyHandler)
	logger.setLevel(level)
	return logger
	


