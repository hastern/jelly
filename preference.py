#!/usr/bin/env python
# -*- coding:utf-8 -*-


"""Helper function to append a preference path inside the user home"""

import os
import sys
import time
from collections import OrderedDict

def escapeString(s):
	s = s.replace("\033","\\033")
	#s = s.replace("\n","\\n")
	#s = s.replace("\t","\\t")
	#s = s.replace("\r","\\r")
	return s
def unescapeString(s):
	s = s.replace("\\033","\033")
	return s

class ConfigurationValueInvalidError(Exception):
	"""The validation of the value has failed"""

class ConfigurationValue(object):
	def __init__(self, default, help = "", t = None, min = None, max = None, choices = None, validation = None, custom = False):
		self.value = default
		self.default = default if not custom else None
		self.help = help
		self.type = t if t is not None else type(self.value)
		self.min = min if min is not None else 0
		self.max = max if max is not None else sys.maxint
		self.choices = choices
		self.custom = custom
		if validation is None:
			if self.choices is not None:
				validation = lambda v,choices=self.choices: v in choices
			elif min is not None and max is not None:
				validation = lambda v,min=min, max=max: min <= v <= max
			else:
				validation = lambda v: True
		assert callable(validation)
		self.validation = validation
		self.name = ""
		
	def setName(self, name):
		self.name = name
		return self
		
	def set(self, value):
		if self.validation(value):
			if isinstance(self.value, dict):
				self.value.update(value)
			else:
				self.value = value
		else:
			raise ConfigurationValueInvalidError(self.name, value)
		return self
			
	def get(self):
		return self.value
		
	def __str__(self):
		s = "#{}\n".format(self.help) if self.help != "" else ""
		s += "{} = {}\n".format(self.name, repr(self))
		return s
	def __repr__(self):
		if self.value.__class__ is str or self.type is str:
			return "\"{}\"".format(escapeString(str(self.value)))
		else:
			return "{}".format(escapeString(str(self.value)))
			
	def __eq__(self, other):
		return isinstance(other, ConfigurationValue) and self.get() == other.get()
		
	@property
	def isModified(self):
		return self.custom or self.value != self.default
		
	@property
	def kind(self):
		return ConfigurationValue

class ConfigurationDict(ConfigurationValue):
	def __init__(self, items, help, custom = False):
		entries = {key:ConfigurationValue(val).setName(key) if not isinstance(val,ConfigurationValue) else val for key, val in items.iteritems()}
		ConfigurationValue.__init__(self, entries, help, t=dict, custom = custom)
		if not custom:
			self.defaults = dict()
			self.defaults.update(items)
			
	def __str__(self):
		s = "# {}\n".format(self.help)
		s += "{} = {}".format(self.name, repr(self))
		return s
	def __repr__(self):
		s = "{{\n".format(self.name)
		for key, val in self.values.iteritems():
			if val.__class__ is str or val.type is str:
				s += "\t'{}' : \"{}\",\n".format(key, escapeString(str(val.get())))
			else:
				s += "\t'{}' : {},\n".format(key, escapeString(str(val.get())))
		s += "}\n\n"
		return s
		
	def set(self, values):
		for key,val in values.iteritems():
			if isinstance(self.values[key], ConfigurationValue):
				self.values[key].set(val)
			else:
				self.values[key] = val
		return self
			
	
	def get(self, key=None):
		return self if key is None else self[key]
		
	def keys(self):
		return self.values.keys()
		
	def __getattr__(self, attr):
		if attr in self:
			return self[attr]
		else:
			raise AttributeError(attr)
		
	def __getitem__(self, key):
		return self.values[key].get()
	
	def __contains__(self, key):
		return key in self.values
		
	def __iter__(self):
		for key in self.values:
			yield key
		raise StopIteration()
			
	def itervalues(self):
		for val in self.values.itervalues():
			yield val.get()
		raise StopIteration()
		
	def iteritems(self):
		for key,val in self.values.iteritems():
			yield key,val
		raise StopIteration()
	
	@property
	def values(self):
		return self.value
		
	@property
	def isModified(self):
		return self.custom or any([self.defaults[key] != self.values[key].get() for key in self.values])

	def getKind(self, entry):
		return self.values[entry].kind if entry in self.values else None		
		
	@property
	def kind(self):
		return ConfigurationDict	
		
class ConfigurationValueList(ConfigurationDict):
	def __init__(self, items, help = "", appendable = True, contentType = None, custom = False):
		ConfigurationDict.__init__(self, items, help, custom)
		self.appendable = appendable
		self.contentType = contentType
		
	@property
	def kind(self):
		return ConfigurationValueList	
		
class UserPreferenceMeta(type):
	"""Metaclass for User Preference"""
	
	def __init__(cls, name, bases, attrs):
		if not hasattr(cls, "__host__"):
			setattr(cls, "__host__", cls)
		if hasattr(cls, "__prefix__"):
			dst = OrderedDict()
		else:
			dst = cls.__host__.__values__
		for member in cls.__dict__:
			if not member.startswith("_"):
				value = getattr(cls, member)
				if not callable(value):
					dst[member] = value.setName(member)
		if hasattr(cls, "__prefix__"):
			cls.__host__.__values__[cls.__prefix__] = ConfigurationDict(dst, help=cls.__doc__)
					
class UserPreference(object):
	__metaclass__ = UserPreferenceMeta
	__values__ = OrderedDict()

	def __init__(self, appname):
		if sys.platform == "win32":
			self.appdata = os.path.join(os.environ['APPDATA'], appname)
		else:
			self.appdata = os.path.expanduser(os.path.join("~", appname))
		self.appname = appname
		self.configfile = None
		self.modules = {}
		
	def addModules(self, **modules):
		self.modules.update(modules)
		return self
		
	def add(self, name, entry):
		assert isinstance(entry, ConfigurationValue)
		self.values[name] = entry
		return self
		
	def addMany(self, entries):
		for name, entry in entries.iteritems():
			self.add(name, entry)
		return self
		
	def load(self, configfile = "pref.py"):
		entries = dict()
		self.configfile = configfile
		customPref = os.path.join(self.appdata, self.configfile)
		if os.path.exists(customPref):
			execfile(customPref, self.modules, entries)
		for key, val in entries.iteritems():
			if key in self.__values__:
				self.__values__[key].set(val)
			else:
				self.__values__[key] = ConfigurationValue(key, val, custom = True)
		return self
		
	def save(self, configfile = "pref.py"):
		customPref = os.path.join(self.appdata, self.configfile)
		if not os.path.exists(os.path.basename(customPref)):
			os.makedirs(os.path.basename(customPref))
		fHnd = open(customPref, "w")
		fHnd.write(str(self))
		fHnd.close()
		
	def __str__(self):
		s = ""
		s += "#!/usr/bin/env python\n"
		s += "# -*- coding:utf-8 -*-\n"
		s += "\n"
		s += "# Custom User Preference for {}\n".format(self.appname)
		s += "# \n"
		s += "# Last modification: {}\n".format(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
		s += "# \n"
		s += "\n"
		for val in self.__values__.itervalues():
			if val.isModified:
				s += str(val)
		return s
	__repr__ = __str__
		
	def getKind(self, entry):
		return self.__values__[entry].kind if entry in self.__values__ else None
		
	def __getattr__(self, attr):
		if attr in self:
			return self[attr]
		else:
			raise AttributeError(attr)
		
	def __getitem__(self, key):
		return self.__values__[key].get()
	
	def __contains__(self, key):
		return key in self.__values__
		
	def __iter__(self):
		for key in self.__values__:
			yield key
		raise StopIteration()
			
	def itervalues(self):
		for val in self.__values__.itervalues():
			yield val
		raise StopIteration()
	def iteritems(self):
		for key,val in self.__values__.iteritems():
			yield key,val
		raise StopIteration()
		