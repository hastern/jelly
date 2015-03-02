#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jelly Shortcuts

"""


import logging
# We are assuming, that there is an already configured logger present
logger = logging.getLogger(__name__)

class ShortcutBuilder(object):
    """Mixin to be used alongside a menubuilder or a viewbuilder"""
    
    def registerShortcuts(self, childs):
        """Register a set of shortcuts"""
        self.sc_childs = childs
    
    def getShortcuts(self):
        """Iterator over all shortcuts from every child"""  
        if self.isMount():
            if self.sc_childs is not None:
                for child in self.sc_childs:
                    for sc in child.getShortcuts():
                        yield sc
                raise StopIteration()
        else:
            raise StopIteration()
            
    def getShortcutIds(self):
        """Iterator over all IDs from every shortcuts from every child"""
        if self.isMount():
            if self.sc_childs is not None:
                for child in self.sc_childs:
                    for sc in child.getShortcutIds():
                        yield sc
                raise StopIteration()
        else:
            raise StopIteration()

