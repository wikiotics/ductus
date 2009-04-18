from ductus.resource import models, register_model

class OptionalTextElement(models.TextElement):
    optional = True

    def is_null_xml_element(self):
        return not self.text

class OptionalLinkElement(models.LinkElement):
    optional = True

    def is_null_xml_element(self):
        return not self.href

class CreditElement(models.Element):
    ns = 'http://wikiotics.org/ns/2009/credit'
    nsmap = {'credit': ns}

    title = OptionalTextElement()
    original_url = OptionalLinkElement()
    author = OptionalTextElement()
    author_url = OptionalLinkElement()

def rotation_validator(v):
    if not v in (None, '', '0', '90', '180', '270'):
        raise models.ValidationError

class Picture(models.Model):
    ns = 'http://wikiotics.org/ns/2009/picture'
    blob = models.TypedBlobElement(allowed_mime_types=['image/jpeg'])
    credit = CreditElement()
    rotation = models.Attribute(optional=True, blank_is_null=True,
                                validator=rotation_validator)

register_model(Picture)
