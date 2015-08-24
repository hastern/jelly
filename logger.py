#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Jelly utilities the python logging facility.
Every module assumes that a properly configured hierarchical logger is present.
This module provides a function to create such a logger without the need to
know anything about the python logging facility.
"""

import re
import logging

from event import EventBase


class JellyLogEvent(EventBase):
    __slots__ = ['record', 'message']


class JellyEventLogHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    @JellyLogEvent.dispatcher
    def emit(self, record):
        s = self.format(record)
        return record, s


class JellyColorLogFormatter(logging.Formatter):
    NO_COLOR = {"DEBUG": "",
                "INFO": "",
                "WARNING": "",
                "ERROR": "",
                "CRITICAL": "",
                "RESET": ""}

    def __init__(self, fmt, colors={}):
        logging.Formatter.__init__(self, fmt)
        self.colors = colors

    def format(self, record):
        msg = logging.Formatter.format(self, record)

        if record.levelname in self.colors:
            msg = msg.replace("$_LEVEL", self.colors[record.levelname])
        if "RESET" in self.colors:
            msg = msg.replace("$_RESET", self.colors['RESET'])
        if "STRING" in self.colors:
            single = re.compile("'([^']*)'")
            double = re.compile('"([^"]*)"')
            msg = single.sub("{}'\\1'{}".format(self.colors['STRING'], self.colors['RESET']), msg)
            msg = double.sub('{}"\\1"{}'.format(self.colors['STRING'], self.colors['RESET']), msg)
        if "POINTER" in self.colors:
            pat = re.compile("0x([0-9A-Fa-f]+)")
            msg = pat.sub('{}0x\\1{}'.format(self.colors['POINTER'], self.colors['RESET']), msg)
        if "REPR" in self.colors:
            pat = re.compile("<([^']*)>")
            msg = pat.sub("<{}\\1{}>".format(self.colors['REPR'], self.colors['RESET']), msg)
        if "BRACKET" in self.colors:
            pat = re.compile("([\(\)\{\}])")
            msg = pat.sub("{}\\1{}".format(self.colors['BRACKET'], self.colors['RESET']), msg)
        # if "SYMBOL" in self.colors:
        #     pat = re.compile("([^0-9])([-:.+*/,;])([^0-9])")
        #     msg = pat.sub("\\1{}\\2{}\\3".format(self.colors['SYMBOL'], self.colors['RESET']), msg)
        return msg


def configureLogger(name="jelly", formatString='%(asctime)s [$_LEVEL%(levelname)s$_RESET] %(name)s: $_LEVEL%(message)s$_RESET', level=logging.DEBUG, colors=None):
    """
    Configure a logger for the python logging facility.

    @type  name: str
    @param name: The name of the logger

    @type  formatString: string
    @param formatString: The format string for the logging output.

    @type  level: int
    @param level: The loglevel

    @type  colored: bool
    @param colored: Should the output be colored?

    @return: the logger instance
    @rtype:  logging.Logger
    """
    logger = logging.getLogger(name)
    streamHandler = logging.StreamHandler()
    jellyHandler = JellyEventLogHandler()
    if colors is not None:
        streamHandler.setFormatter(JellyColorLogFormatter(formatString, colors))
    else:
        streamHandler.setFormatter(JellyColorLogFormatter(formatString, JellyColorLogFormatter.NO_COLOR))
    jellyHandler.setFormatter(JellyColorLogFormatter(formatString, JellyColorLogFormatter.NO_COLOR))
    logger.addHandler(streamHandler)
    logger.addHandler(jellyHandler)
    logger.setLevel(level)
    return logger
