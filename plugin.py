#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jelly Plugin - A minimal plugin framework.

The idea and basis for this code came from: 
http://martyalchin.com/2008/jan/10/simple-plugin-framework/

To create a pluginhook define a new class, and set `PluginMount` or 
`TaxonomyPluginMount` as its `__metaclass__`. 

Every plugin must be a child of the pluginhook, inheriting its interface.
Therefore no special interface declaration is necessary. 


"""

import logging
# We are assuming, that there is an already configured logger present
logger = logging.getLogger(__name__)

def createPluginsFolder(dirname = 'plugins'):
	"""Create a plugin folder in the current working directory,
	if none is existent.
	
	@type  dirname: str
	@param dirname: The name for the plugin-directory
	"""
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
	if not os.path.exists(name):
		os.mkdir(name)
		open("{}/__init__.py".format(name), "w").write(pluginInit)

class PluginMount(type):
	"""A simple pluginMount. 
	To hook a plugin into the mount, simply let your object inherit from it.
	"""
	def __init__(cls, name, bases, attrs):		
		"""The first object to be initialized is always the parent.
		Due to the way class-members are accessed, all children of this 
		object hook themself into the mounts plugin list. Thereby 
		getting visible to the mount.
		
		@type  cls: type
		@param cls: The class object to be initialized.
		
		@type  name: str
		@param name: The name of the class object.
		
		@type  bases: list
		@param bases: A list of base classes for the class object
		
		@type  attrs: list
		@param attrs: A list of attributes for the class object
		"""
		if not hasattr(cls, 'plugins'):
			logger.debug("Creating pluginmount {}".format(cls.__name__))
			# Create plugin list
			cls.plugins = []
			# Set self as base class 
			cls.base = cls
		else:
			logger.debug("Registering plugin {}".format(cls.__name__))
			# Append self to plugin list 
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
		"""Like the `PluginMount` the first object to be initialized 
		will become the mount, any later objects (meaning: childs) 
		act as plugins.
		
		The taxonomy is created via nested dictionaries.
		Each plugin can define a class-member `__category__`.
		The Elements of the hierarchy are separated by a single dot.
		
		@type  cls: object
		@param cls: The class object to be initialized.
		
		@type  name: str
		@param name: The name of the class object.
		
		@type  bases: list
		@param bases: A list of base classes for the class object
		
		@type  attrs: list
		@param attrs: A list of attributes for the class object
		"""
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
		"""Lookup for a fully qualified class name
		
		@type  cls: object
		@param cls: The hook class
		
		@type  clazz: str
		@param clazz: The name of the class to be looked up.
		
		@type  categories: list
		@param categories: The hierarchy in which the class is ordered.
		
		@rtype:  object
		@return: The class
		"""
		taxonomy = cls.taxonomy
		for category in categories:
			taxonomy = taxonomy[category]
		return taxonomy[clazz]
		
	def __getitem__(cls, key):
		"""Implementation of the Indexed-Access-Operator (`[]`).
		Delegating to a call of `TaxonomyPluginMount.findClass`.
		
		@type  cls: object
		@param cls: The hook class
		
		@type  key: str
		@param key: The fully qualified class name 
		
		@rtype:  object
		@return: The class
		"""
		categories = key.split('.')
		clazz = categories.pop()
		return cls.findClass(clazz, categories)
		
	def getFQClassName(cls):
		"""
		@type  cls: object
		@param cls: A Class object
		
		@rtype:  str
		@return: the fully qualified class name of a class
		"""
		if cls.__category__ != "":
			return ".".join((cls.__category__,cls.__name__))
		else:
			return cls.__name__
		
