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

    def __new__(cls, *args, **kwargs):
        self = super(Structure, cls).__new__(cls, *args, **kwargs)
        # Initialize all members with None
        map(lambda k: setattr(self, k, cls.__defaults__[k]() if k in cls.__defaults__ else None), cls.__slots__)
        return self

    def __init__(self, *args, **kwargs):
        """
        @param    *args:   Positional arguments
        @param **kwargs: Keyword arguments
        """
        # Positional definition of members
        map(lambda (name, val): setattr(self, name, val), zip(self.__slots__, args))
        # Keyword definition of members
        map(lambda k: setattr(self, k, kwargs[k]), filter(lambda k: k in self.__slots__, kwargs))

    @property
    def kind(self):
        return self.__class__

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.__slots__ != other.__slots__:
            return False
        for attr in self.__slots__:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True


class EnumValue(object):
    """Value for an enumeration"""
    def __init__(self, host, name, value):
        """Create a new enumeration value"""
        self.host = host
        """The class hosting this value"""
        self.name = name
        """Its name"""
        self.value = value
        """Its value"""
    def __eq__(self, other):
        return other == self.value

    def __str__(self):
        return "{c.host.__name__}.{c.name}".format(c=self)

    def __repr__(self):
        return str(self.value)

    def __int__(self):
        return self.value


class EnumMeta(type):
    """Metaclass for enumeration creation"""
    def __init__(cls, *args):
        for member in cls.__dict__:
            if not member.startswith("_"):
                value = getattr(cls, member)
                setattr(cls, member, EnumValue(cls, member, value))

    def __repr__(cls):
        """Create the string representation"""
        str = "{}(Enumeration):\n".format(cls.__name__)
        str += '\t"""{}"""\n'.format(cls.__doc__)
        for member in cls.__dict__:
            if not member.startswith("_"):
                val = getattr(cls, member)
                str += "\t{v.name:} = {v.value:}\n".format(v=val)
        return str

    def __iter__(cls):
        for member in cls.__dict__:
            if not member.startswith("_"):
                yield getattr(cls, member)

    @property
    def items(cls):
        return [itm for itm in cls]

    @property
    def entries(cls):
        return {int(itm): itm.name for itm in cls}

    def fromString(cls, s):
        for itm in cls:
            if s == str(itm):
                return itm

    def toString(cls, i):
        for itm in cls:
            if i == itm.value:
                return str(itm)


class Enumeration(object):
    """An enumeration like object"""
    __metaclass__ = EnumMeta
