#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Jelly utilities the python logging facility.
Every module assumes that a properly configured hierarchical logger is present.
This module provides a function to create such a logger without the need to 
know anything about the python logging facility.
"""

import logging

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
	handler = logging.StreamHandler()
	formatter = logging.Formatter(formatString)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(level)
	return logger
