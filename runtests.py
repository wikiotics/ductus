#!/usr/bin/env python

# We use our own test script for now, until Django #10853 is fixed.

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ductus.settings")

import ductus.util
import ductus.util.bcp47
import ductus.license

import unittest, doctest

suite = unittest.TestSuite()
for mod in ductus.util, ductus.util.bcp47, ductus.license:
    suite.addTest(doctest.DocTestSuite(mod))

runner = unittest.TextTestRunner()
runner.run(suite)
