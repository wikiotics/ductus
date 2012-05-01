#!/usr/bin/env python

# We use our own test script for now, until Django #10853 is fixed.

if __name__ == "__main__":
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ductus.settings")

    import pytest
    pytest.main(["ductus", "--doctest-modules"])
