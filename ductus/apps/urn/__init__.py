def get_resource_database():
    global __resource_database
    if __resource_database is None:
        from django.conf import settings
        backend = settings.DUCTUS_STORAGE_BACKEND
        mod_name, junk, var_name = backend.rpartition('.')
        __resource_database = getattr(__import__(mod_name, {}, {}, ['']),
                                      var_name)
    return __resource_database

__resource_database = None
