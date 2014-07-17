#!/usr/bin/env python
# -*- coding:utf-8 -*-


"""Helper function to append a preference path inside the user home"""

import os
import sys
import time
from collections import OrderedDict

spam = "eggs"

def escapeString(s):
	s = s.replace("\033","\\033")
	s = s.replace("\n","\\n")
	s = s.replace("\t","\\t")
	s = s.replace("\r","\\r")
	return s

class ConfigurationValueInvalidError(Exception):
	"""The validation of the value has failed"""

class ConfigurationValue(object):
	def __init__(self, name, value, help = "", t = None, min = None, max = None, choices = None, validation = None, custom = False):
		self.name = name
		self.value = value
		self.default = value if not custom else None
		self.help = help
		self.type = t if t is not None else type(value)
		self.min = min
		self.max = max
		self.choices = None
		self.custom = custom
		if validation is None:
			if self.choices is not None:
				validation = lambda v: v in self.choices
			elif self.min is not None and self.max is not None:
				validation = lambda v: self.min <= v <= self.max
			else:
				validation = lambda v: True
		assert callable(validation)
		self.validation = validation
		
	def set(self, value):
		if self.validation(value):
			self.value = value
		else:
			raise ConfigurationValueInvalidError(value)
			
	def get(self):
		return self.value
		
	def __str__(self):
		if self.value.__class__ is dict:
			s = "# {}\n".format(self.help)
			s += "{} = {{\n".format(self.name)
			for key, val in self.value.iteritems():
				if val.__class__ is str:
					s += "\t'{}' : \"{}\",\n".format(key, escapeString(str(val)))
				else:
					s += "\t'{}' : {},\n".format(key, str(val))
			s += "}\n\n"
			return s
		elif self.value.__class__ is str:
			return "#{}\n{} = \"{}\"\n\n".format(self.help, self.name, escapeString(str(self.value)))
		else:
			return "#{}\n{} = {}\n\n".format(self.help, self.name, str(self.value))
	__repr__ = __str__
		
	@property
	def isModified(self):
		return self.custom or self.value != self.default
		

class UserPreferenceLoader(object):

	def __init__(self, appname):
		if sys.platform == "win32":
			self.appdata = os.path.join(os.environ['APPDATA'], appname)
		else:
			self.appdata = os.path.expanduser(os.path.join("~", appname))
		self.appname = appname
		self.configfile = None
		self.values = OrderedDict()
		self.modules = {}
		
	def addModules(self, **modules):
		self.modules.update(modules)
		return self
		
	def add(self, *entries):
		for entry in entries:
			assert isinstance(entry, ConfigurationValue)
			self.values[entry.name] = entry
		return self
		
	def load(self, configfile = "pref.py"):
		entries = dict()
		self.configfile = configfile
		customPref = os.path.join(self.appdata, self.configfile)
		if os.path.exists(customPref):
			execfile(customPref, self.modules, entries)
		for key, val in entries.iteritems():
			if key in self.values:
				self.values[key].set(val)
			else:
				self.values[key] = ConfigurationValue(key, val, custom = True)
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
		for val in self.values.itervalues():
			if val.isModified:
				s += str(val)
		return s
	__repr__ = __str__
		
	def __getattr__(self, attr):
		if attr in self:
			return self[attr]
		
	def __getitem__(self, key):
		return self.values[key].get()
	
	def __contains__(self, key):
		return key in self.values
		

