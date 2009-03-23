from ductus.resource import models, register_model

class OptionalTextElement(models.TextElement):
    optional = True

    def is_null_xml_element(self):
        return not self.text

class OptionalLinkElement(models.LinkElement):
    optional = True

    def is_null_xml_element(self):
        return not self.href

class Credit(models.Element):
    ns = 'http://wikiotics.org/ns/2009/credit'
    nsmap = {'credit': ns}
    fqn = "{%s}credit" % ns

    title = OptionalTextElement()
    original_url = OptionalLinkElement()
    author = OptionalTextElement()
    author_url = OptionalLinkElement()

class Picture(models.Model):
    ns = 'http://wikiotics.org/ns/2009/picture'
    blob = models.TypedBlobElement(allowed_mime_types=['image/jpeg'])
    credit = Credit()

register_model(Picture)
