#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging

def configureLogger(name = "jelly", formatString = '%(asctime)s [%(levelname)s] %(name)s: %(message)s', level = logging.DEBUG):
	logger = logging.getLogger(name)
	handler = logging.StreamHandler()
	formatter = logging.Formatter(formatString)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(level)
	return logger
