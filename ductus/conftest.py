# see http://pytest.org/latest/example/simple.html#detect-if-running-from-within-a-py-test-run

def pytest_configure(config):
    import ductus
    ductus._called_from_test = True

def pytest_unconfigure(config):
    import ductus
    del ductus._called_from_test
