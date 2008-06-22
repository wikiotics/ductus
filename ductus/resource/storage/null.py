class NullStorageBackend(object):
    """Pointless storage backend.  Always contains nothing.

    May actually be useful for testing other backends, such as
    UnionStorageBackend.
    """

    def __contains__(self, key):
        return False
    def put_file(self, key, filename):
        raise Exception("Can't save anything to the null storage backend")
    def __getitem__(self, key):
        raise KeyError(key)
    def __delitem__(self, key):
        raise KeyError(key)
    def keys(self):
        return []
    def iterkeys(self):
        return iter([])
    __iter__ = iterkeys
    def __len__(self):
        return 0
