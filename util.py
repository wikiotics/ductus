from __future__ import with_statement

def iterate_file(filename):
    with file(filename) as f:
        while True:
            x = f.read(4096)
            if x == '':
                return
            yield x
