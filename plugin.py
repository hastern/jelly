#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
# We are assuming, that there is an already configured logger present
logger = logging.getLogger(__name__)

# This will auto-create the plugin directory if none is existent
import os

pluginInit = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
del module
"""

if not os.path.exists("plugins"):
	os.mkdir("plugins")
	open("plugins/__init__.py", "w").write(pluginInit)

class PluginMount(type):
	"""A simple pluginMount. 
	To hook a plugin into the mount, simply let your object inherit from it.
	
	The idea for this came from: 
	http://martyalchin.com/2008/jan/10/simple-plugin-framework/"""
	def __init__(cls, name, bases, attrs):		
		"""The first object to be initialised is always the parent.
		Due to the way class-members are access, all children of this 
		object hook them self into the mounts plugin list"""
		if not hasattr(cls, 'plugins'):
			logger.debug("Creating pluginmount {}".format(cls.__name__))
			cls.plugins = []
			cls.base = cls
		else:
			logger.debug("Registering plugin {}".format(cls.__name__))
			cls.plugins.append(cls)
		cls.isMount = lambda self: self.base is self.__class__
		cls.isPlugin = lambda self: self.base is not self.__class__	
		
	def loadPlugins(cls, *args, **kwargs):
		"""Create a list of instantiated plugins
		if this is not called from inside the mount instance, you should
		specify the *caller* argument, to avoid double instantiation of 
		your child class""" 
		caller = kwargs['caller'].__class__ if 'caller' in kwargs else None
		return [p(*args, **kwargs) for p in cls.plugins if p is not caller]
		
class TaxonomyPluginMount(type):
	"""PluginMount for plugins with a taxonomy on its plugins
	To hook a plugin into the mount, let your object inherit from it."""
	
	def __init__(cls, name, bases, attrs):
		if not hasattr(cls, 'taxonomy'):
			logger.debug("Creating TaxonomyPluginMount {}".format(cls.__name__))
			cls.taxonomy = {}
			cls.__category__ = ""
		else:
			logger.debug("Registering plugin {} into taxonomy {}".format(cls.__name__, cls.__category__))
			taxonomy = cls.taxonomy
			if cls.__category__ != "":
				for category in cls.__category__.split('.'):
					if category not in taxonomy:
						taxonomy[category] = {}
					taxonomy = taxonomy[category]
			taxonomy[cls.__name__] = cls
			
	def findClass(cls, clazz, categories):
		taxonomy = cls.taxonomy
		for category in categories:
			taxonomy = taxonomy[category]
		return taxonomy[clazz]
		
	def __getitem__(cls, key):
		categories = key.split('.')
		clazz = categories.pop()
		return cls.findClass(clazz, categories)
		
