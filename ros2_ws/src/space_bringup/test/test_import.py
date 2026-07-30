import importlib
import unittest


class TestImport(unittest.TestCase):
    def test_package_imports(self):
        self.assertIsNotNone(importlib.import_module('space_bringup'))
