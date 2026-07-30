import importlib
import unittest


class TestImport(unittest.TestCase):
    def test_depth_overlay_module_imports(self):
        self.assertIsNotNone(importlib.import_module('space_perception.depth_overlay_node'))
