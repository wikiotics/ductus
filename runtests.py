#!/usr/bin/env python

# We use our own test script for now, until Django #10853 is fixed.

if __name__ == "__main__":
    # initialize ductus
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ductus.settings")
    import ductus.initialize

    # perform the tests
    import pytest
    pytest.main(["--doctest-modules", "ductus", "tests"])
