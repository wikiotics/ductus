def get_resource_database():
    global __resource_database
    if __resource_database is None:
        from django.conf import settings
        backend = settings.DUCTUS_STORAGE_BACKEND
        mod_name, junk, var_name = backend.rpartition('.')
        storage_backend = getattr(__import__(mod_name, {}, {}, ['']),
                                      var_name)
        from ductus.resource import ResourceDatabase
        __resource_database = ResourceDatabase(storage_backend)
    return __resource_database

__resource_database = None
