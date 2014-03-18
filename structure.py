#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
# We are assuming, that there is an already configured logger present
logger = logging.getLogger(__name__)

class Structure(object):
	"""Simple struct-like object.
	members are controlled via the contents of the __slots__ list."""
	__slots__ = []
	"""Structure members"""
	__defaults__ = {}
	"""Default values for (a part of) the structure members. 
	__defaults__.keys() must be a (inproper) subset __slots__."""
	def __init__(self, *args, **kwargs):
		"""
		@param	*args:   Positional arguments
		@param **kwargs: Keyword arguments
		"""
		# Initialize all members with None
		map(lambda k: self.__setattr__(k, self.__defaults__[k]() if k in self.__defaults__ else None), self.__slots__)
				
		# Positional definition of members
		for i,a in enumerate(args):
			if len(self.__slots__) > i:
				self.__setattr__(self.__slots__[i], a)
		# Keyword definition of members
		map(lambda k: self.__setattr__(k, None), filter(lambda k: k in self.__slots__, kwargs))