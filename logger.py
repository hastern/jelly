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
		
class JellyColorLogFormatter(logging.Formatter):
	RESET   = "\033[0m"
	TIME    = "\033[37m"
	MESSAGE = "\033[37m"
	LEVELS = {
		"DEBUG"    : "\033[36m",
		"INFO"     : "\033[37m",
		"WARNING"  : "\033[33m",
		"ERROR"    : "\033[1;31m",
		"CRITICAL" : "\033[41;37m",
	}
	def __init__(self, fmt, use_color = True):
		if not use_color:
			fmt = fmt.replace("$_TIME","").replace("$_RESET","").replace("$_LEVEL","").replace("$_MESSAGE","")
		logging.Formatter.__init__(self, fmt)
	def format(self, record):
		msg = logging.Formatter.format(self, record)
		msg = msg.replace("$_LEVEL", self.LEVELS[record.levelname])
		msg = msg.replace("$_MESSAGE", self.MESSAGE)
		msg = msg.replace("$_TIME", self.TIME)
		msg = msg.replace("$_RESET", self.RESET)
		return msg

def configureLogger(name = "jelly", formatString = '$_TIME%(asctime)s$_RESET [$_LEVEL%(levelname)s$_RESET] %(name)s: $_MESSAGE%(message)s$_RESET', level = logging.DEBUG, colored = True):
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
	if colored:
		streamHandler.setFormatter(JellyColorLogFormatter(formatString))
	else:
		streamHandler.setFormatter(JellyColorLogFormatter(formatString, False))
	jellyHandler.setFormatter(JellyColorLogFormatter(formatString, False))
	logger.addHandler(streamHandler)
	logger.addHandler(jellyHandler)
	logger.setLevel(level)
	return logger
	


