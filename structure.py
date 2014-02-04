#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)

class Structure(object):
	__slots__ = []
	__defaults__ = {}
	def __init__(self, *args, **kwargs):
		"""
		Constructor for simple struct-like object
		members are controlled via the contents of the __slots__ list.
		
		@param	*args: Positional arguments
		@param **kwargs: Keyword arguments
		"""
		# Initialise all members with None
		map(lambda k: self.__setattr__(k, self.__defaults__[k]() if k in self.__defaults__ else None), self.__slots__)
				
		# Positional definition of members
		for i,a in enumerate(args):
			if len(self.__slots__) > i:
				self.__setattr__(self.__slots__[i], a)
		# Keyword definition of members
		map(lambda k: self.__setattr__(k, None), filter(lambda k: k in self.__slots__, kwargs))