from django.conf import settings

from ductus.resource import models, register_model
from ductus.util import create_property

class WikiBlobElement(models.TextBlobElement):
    allowed_markup_languages = ('creole-1.0',)
    allowed_natural_languages = (None, '') + zip(*settings.DUCTUS_NATURAL_LANGUAGES)[0]
    markup_language = models.Attribute(validator=models.allowed_values_attribute_validator(allowed_markup_languages))
    natural_language = models.Attribute(validator=models.allowed_values_attribute_validator(allowed_natural_languages), optional=True, blank_is_null=True)

    def __init__(self):
        # fixme: if Attribute had a "default" argument, we wouldn't need to
        # override this constructor to set such a default
        super(WikiBlobElement, self).__init__()
        self.markup_language = "creole-1.0"

@register_model
class Wikitext(models.Model):
    ns = 'http://wikiotics.org/ns/2009/wikitext'
    blob = WikiBlobElement()

    @create_property
    def text():
        def fget(s):
            return b''.join(s.blob).decode('utf-8')
        def fset(s, v):
            s.blob.store([v.encode('utf-8')])
        return locals()
