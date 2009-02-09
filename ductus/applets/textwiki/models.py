from ductus.resource import models, register_model
from ductus.util import create_property

class Wikitext(models.Model):
    ns = 'http://wikiotics.org/ns/2009/wikitext'
    blob = models.BlobElement()

    @create_property
    def text():
        def fget(s):
            return ''.join(s.blob.iterate(s.resource_database))
        def fset(s, v):
            s.blob.href = s.resource_database.store_blob([v])
        return locals()

register_model(Wikitext)
