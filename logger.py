#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Jelly utilities the python logging facility.
Every module assumes that a properly configured hierarchical logger is present.
This module provides a function to create such a logger without the need to 
know anything about the python logging facility.
"""

import re
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
		
class JellyColorLogFormatter(logging.Formatter):
	NO_COLOR = {"$_LEVEL":"", "RESET":""}
	def __init__(self, fmt, colors = {}):
		logging.Formatter.__init__(self, fmt)
		self.colors = colors
	def format(self, record):
		msg = logging.Formatter.format(self, record)
		if record.levelname in self.colors:
			msg = msg.replace("$_LEVEL", self.colors[record.levelname])
		if "RESET" in self.colors:
			msg = msg.replace("$_RESET", self.colors['RESET'])
		if "STRING" in self.colors:
			single = re.compile("'([^']*)'")
			double = re.compile('"([^"]*)"')
			msg = single.sub("{}'\\1'{}".format(self.colors['STRING'], self.colors[record.levelname]), msg)
			msg = double.sub('{}"\\1"{}'.format(self.colors['STRING'], self.colors[record.levelname]), msg)
		return msg

def configureLogger(name = "jelly", formatString = '%(asctime)s [$_LEVEL%(levelname)s$_RESET] %(name)s: $_LEVEL%(message)s$_RESET', level = logging.DEBUG, colors = None):
	"""
	Configure a logger for the python logging facility.
	
	@type  name: str
	@param name: The name of the logger
	
	@type  formatString: string
	@param formatString: The format string for the logging output.
	
	@type  level: int
	@param level: The loglevel
	
	@type  colored: bool
	@param colored: Should the output be colored?
	
	@return: the logger instance
	@rtype:  logging.Logger
	"""
	logger = logging.getLogger(name)
	streamHandler = logging.StreamHandler()
	jellyHandler  = JellyEventLogHandler()
	if colors is not None:
		streamHandler.setFormatter(JellyColorLogFormatter(formatString, colors))
	else:
		streamHandler.setFormatter(JellyColorLogFormatter(formatString, JellyColorLogFormatter.NO_COLOR))
	jellyHandler.setFormatter(JellyColorLogFormatter(formatString, JellyColorLogFormatter.NO_COLOR))
	logger.addHandler(streamHandler)
	logger.addHandler(jellyHandler)
	logger.setLevel(level)
	return logger
	


