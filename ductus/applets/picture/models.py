from ductus.resource import models, register_model

allowed_licenses = (
    'http://creativecommons.org/licenses/publicdomain/',
    'http://creativecommons.org/licenses/by-sa/1.0/',
    'http://creativecommons.org/licenses/by-sa/2.0/',
    'http://creativecommons.org/licenses/by-sa/2.5/',
    'http://creativecommons.org/licenses/by-sa/3.0/',
    'http://creativecommons.org/licenses/by/1.0/',
    'http://creativecommons.org/licenses/by/2.0/',
    'http://creativecommons.org/licenses/by/2.5/',
    'http://creativecommons.org/licenses/by/3.0/',
)

class Picture(models.Model):
    ns = 'http://wikiotics.org/ns/2009/picture'
    blob = models.TypedBlobElement(allowed_mime_types=['image/jpeg'])
register_model(Picture)
