class UnsupportedOperation(Exception):
    pass

from ductus.resource.storage.cache import CacheStorageBackend
from ductus.resource.storage.mongogridfs import GridfsStorageBackend
from ductus.resource.storage.local import LocalStorageBackend
from ductus.resource.storage.noop import WrapStorageBackend
from ductus.resource.storage.null import NullStorageBackend
from ductus.resource.storage.remote_ductus import RemoteDuctusStorageBackend
from ductus.resource.storage.safe import SafeStorageBackend
from ductus.resource.storage.union import UnionStorageBackend
from ductus.resource.storage.untrusted import UntrustedStorageBackend, UntrustedStorageMetaclass
