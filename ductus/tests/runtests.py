#!/usr/bin/env python

import unittest, doctest
import ductus.util

suite = unittest.TestSuite()
for mod in ductus.util,:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner()
runner.run(suite)
