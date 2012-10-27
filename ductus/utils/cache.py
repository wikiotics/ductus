"""
Provides a way to use the low-level Django cache API with `snappy' compression
if it is available
"""

from django.core.cache import cache

try:
    from snappy import compress, decompress
    additional_prefix = 'snap:'
except ImportError:
    compress = decompress = lambda value: value
    additional_prefix = ':'

class CacheCompressed(object):
    def set(self, key, value, *args, **kwargs):
        return cache.set(additional_prefix + key, compress(value), *args, **kwargs)

    def get(self, key):
        rv = cache.get(additional_prefix + key)
        if rv is not None:
            rv = decompress(rv)
        return rv

cache_compressed = CacheCompressed()
