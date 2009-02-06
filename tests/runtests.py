#!/usr/bin/env python

import unittest, doctest
import ductus.util, ductus.util.xml

suite = unittest.TestSuite()
for mod in ductus.util, ductus.util.xml:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner()
runner.run(suite)
