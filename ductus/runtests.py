#!/usr/bin/env python

# We use our own test script for now, until Django #10853 is fixed.

import settings # Assumed to be in the same directory.
from django.core.management import setup_environ
setup_environ(settings)

import ductus.util
import ductus.license

import unittest, doctest

suite = unittest.TestSuite()
for mod in ductus.util, ductus.license:
    suite.addTest(doctest.DocTestSuite(mod))

runner = unittest.TextTestRunner()
runner.run(suite)
