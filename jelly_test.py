#!/usr/bin/env python
# -*- coding:utf-8 -*-

import unittest

import structure
import plugin
import event
import baseobjs
import gui
import view
import menu
import shortcut
import logger


class PluginTests(unittest.TestCase):
	
	def testPluginMountAttributes(self):
		class Hook(object):
			__metaclass__ = plugin.PluginMount
			
		self.assertTrue(hasattr(Hook, "plugins"))
		self.assertIs(Hook.plugins.__class__, list)
		self.assertTrue(hasattr(Hook, "base"))
		
	def testPluginMount(self):
		class Hook(object):
			__metaclass__ = plugin.PluginMount
			
		class Plugin(Hook):
			pass
			
		self.assertIn(Plugin, Hook.plugins)	
		
	def testPluginIsMount(self):
		class Hook(object):
			__metaclass__ = plugin.PluginMount
			
		hook = Hook()
		self.assertTrue(hook.isMount())
		self.assertFalse(hook.isPlugin())
		
	def testPluginIsPlugin(self):
		class Hook(object):
			__metaclass__ = plugin.PluginMount
			
		class Plugin(Hook):
			pass
			
		plug = Plugin()
		self.assertTrue(plug.isPlugin())	
		self.assertFalse(plug.isMount())	
		
	def testPluginInstantiation(self):
		class Hook(object):
			__metaclass__ = plugin.PluginMount
			
		class Plugin(Hook):
			pass
			
		plugins = Hook.loadPlugins()
		self.assertEqual(len(plugins), 1)
		self.assertIs(plugins[0].__class__, Plugin)
	
	def testTaxonomyPluginAttributes(self):
		class Hook(object):
			__metaclass__ = plugin.TaxonomyPluginMount
			
		self.assertTrue(hasattr(Hook, "taxonomy"))
		self.assertIs(Hook.taxonomy.__class__, dict)
		self.assertTrue(hasattr(Hook, "__category__"))
		self.assertEqual(Hook.__category__, "")
		
	
	def testTaxonomyPlugin(self):
		class Hook(object):
			__metaclass__ = plugin.TaxonomyPluginMount
			
		class Plugin(Hook):
			pass
			
		self.assertIn(Plugin.__name__, Hook.taxonomy)	
		
	def testTaxonomyPluginCategory(self):
		class Hook(object):
			__metaclass__ = plugin.TaxonomyPluginMount
			
		class Plugin(Hook):
			pass
		
		class CategoryPlugin(Hook):
			__category__ = "category"
			
		self.assertIn(Plugin.__name__, Hook.taxonomy)	
		self.assertIn("{}.{}".format(CategoryPlugin.__category__, CategoryPlugin.__name__), Hook.taxonomy)	
		
	def testTaxonomyPluginInstantiation(self):
		class Hook(object):
			__metaclass__ = plugin.TaxonomyPluginMount
			
		class Plugin(Hook):
			pass
			
		plugins = Hook.loadPlugins()
		self.assertEqual(len(plugins), 1)
		self.assertIn('Plugin', plugins)
		self.assertIs(plugins['Plugin'].__class__, Plugin)
		
	def testTaxonomyPluginSelection(self):
		class Hook(object):
			__metaclass__ = plugin.TaxonomyPluginMount
			
		class Plugin(Hook):
			pass
			
		plug = Hook[Plugin.__name__]()
		self.assertIsNot(plug.__class__, Hook)
		self.assertIs(plug.__class__, Plugin)
	
		
		
class TestStructure(structure.Structure):
	__slots__ = ["foo", "bar", "baz"]

class StructureTests(unittest.TestCase):

	def testPositional(self):
		struct = TestStructure("FOO", "BAR", "BAZ")
		self.assertEqual(struct.foo, "FOO")
		self.assertEqual(struct.bar, "BAR")
		self.assertEqual(struct.baz, "BAZ")
		
	def testKeyword(self):
		struct = TestStructure(foo = "FOO", bar = "BAR", baz = "BAZ")
		self.assertEqual(struct.foo, "FOO")
		self.assertEqual(struct.bar, "BAR")
		self.assertEqual(struct.baz, "BAZ")
		
	def testKeywordMix(self):
		struct = TestStructure(baz = "BAZ", foo = "FOO", bar = "BAR")
		self.assertEqual(struct.foo, "FOO")
		self.assertEqual(struct.bar, "BAR")
		self.assertEqual(struct.baz, "BAZ")
		
	def testMixedArgs(self):
		struct = TestStructure("FOO", baz = "BAZ", bar = "BAR")
		self.assertEqual(struct.foo, "FOO")
		self.assertEqual(struct.bar, "BAR")
		self.assertEqual(struct.baz, "BAZ")
		
	def testPosArgOverrideByPositional(self):
		struct = TestStructure("FOO", "BAR", "BAZ", foo = "FOOBAR")
		self.assertNotEqual(struct.foo, "FOO")
		self.assertEqual(struct.foo, "FOOBAR")
		self.assertEqual(struct.bar, "BAR")
		self.assertEqual(struct.baz, "BAZ")
	
	def testKind(self):
		struct = TestStructure()
		self.assertIs(struct.kind, TestStructure)
		self.assertIsNot(struct.kind, structure.Structure)
		

def main():
	unittest.main(verbosity=2)
	
if __name__ == "__main__":
	main()


