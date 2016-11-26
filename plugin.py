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


def createPluginsFolder(dirname='plugins'):  # pragma: no cover
    """Create a plugin folder in the current working directory,
    if none is existent.

    @type  dirname: str
    @param dirname: The name for the plugin-directory
    """
    import os
    import os.path
    pluginInit = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
__import__(module[:-3], locals(), globals())
del module
"""
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        open("{}/__init__.py".format(dirname), "w").write(pluginInit)


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

    def __iter__(self):
        """Iterate all plugins
        """
        for plugin in self.plugins:
            yield plugin


class TaxonomyPluginMount(type):
    """PluginMount for plugins with a taxonomy on its plugins
    To hook a plugin into the mount, let your object inherit from it."""

    def __init__(cls, name, bases, attrs):
        """Like the `PluginMount` the first object to be initialized
        will become the mount, any later objects (meaning: childs)
        act as plugins.

        The taxonomy is created through a dictionary.
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
            cls.taxonomy[cls.FQClassName] = cls

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
        return cls.taxonomy[key]

    def __iter__(cls):
        """ Iterate the class object to get all plugins
        """
        for key, plugin in cls.taxonomy.items():
            yield plugin

    def getFQClassName(cls):
        """
        @type  cls: object
        @param cls: A Class object

        @rtype:  str
        @return: the fully qualified class name of a class
        """
        if cls.__category__ != "":
            return ".".join((cls.__category__, cls.__name__))
        else:
            return cls.__name__

    @property
    def FQClassName(cls):
        """Remapping getter method to a property"""
        return cls.getFQClassName()

    def loadPlugins(cls, *args, **kwargs):
        """Create a list of instantiated plugins
        if this is not called from inside the mount instance, you should
        specify the *caller* argument, to avoid double instantiation of
        your child class"""
        caller = kwargs['caller'].__class__ if 'caller' in kwargs else None
        return {key: clazz(*args, **kwargs) for key, clazz in cls.taxonomy.items() if key is not caller}

    def getAllCategories(cls, exclude=[]):
        """Create a dictionary with all categories and the class per
        category.
        Returns a dictionary where the keys are the full category with
        a list of class names as values.

        @type  exclude: list
        @param exclude: List of categories to be excluded
        """
        d = {}
        for k, e in map(lambda s: s.rsplit(".", 1), cls.taxonomy.keys()):
            if k not in exclude:
                d[k] = [e] if k not in d else d[k] + [e]
        return d


class MixinMount(type):
    """Metaclass to mix all child methods into the base parent.
    Every child class object will be a reference to the base object.

    The init functions of all childrens will be called consecutivly.
    """

    def __new__(cls, name, bases, attrs):
        """Override the __new__ method the create a singleton class
        object"""
        def init(self, *args, **kwargs):
            """Call all initializer method of all child functions"""
            for init in self.__init_collection__:
                init(self, *args, **kwargs)

        if not hasattr(cls, "instance"):
            # 1. Object -> Base class: create class object instance
            if "__init__" in attrs:
                attrs['__init_collection__'] = [attrs['__init__']]
            else:
                attrs['__init_collection__'] = []
            attrs['__init__'] = init
            logger.debug("Creating mixinmount {}".format(name))
            cls.instance = super(MixinMount, cls).__new__(cls, name, bases, attrs)
        else:
            # Every other object: Append all non-dunderscore methods
            logger.debug("Appending methods from '{}' to {}".format(name, cls.instance))
            if "__init__" in attrs:
                cls.instance.__init_collection__.append(attrs["__init__"])
            for name, attr in attrs.items():
                if not name.startswith("__"):
                    if hasattr(cls.instance, name):
                        logger.warning("Member '{}' already exists in {}".format(name, cls.instance))
                    setattr(cls.instance, name, attr)
        # Emulate multi inheritance
        if len(bases) > 1:
            for base in bases:
                if base != cls.instance:
                    for name, member in base.__dict__.items():
                        if not name.startswith("__"):
                            if hasattr(cls.instance, name):
                                logger.warning("Mixin-member '{}' from {} already exists in {}".format(name, base, cls.instance))
                            setattr(cls.instance, name, member)
                            logger.warning("Mixin '{}' from {} into {}".format(name, base, cls.instance))
        return cls.instance
