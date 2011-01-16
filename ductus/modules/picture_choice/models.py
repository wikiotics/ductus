from ductus.resource import models, register_model
from ductus.modules.picture.models import Picture
from ductus.modules.audio.models import Audio

_ns = 'http://wikiotics.org/ns/2009/picture_choice'

class OptionalResourceElement(models.ResourceElement):
    optional = True

    def is_null_xml_element(self):
        return not self.href

class PictureChoiceElement(models.Element):
    ns = _ns
    nsmap = {'picture_choice': ns}

    phrase = models.TextElement()
    picture = models.ResourceElement(Picture)

    audio = OptionalResourceElement(Audio)

@register_model
class PictureChoiceGroup(models.Model):
    ns = _ns
    nsmap = {'picture_choice': ns}

    group = models.ArrayElement(PictureChoiceElement(), min_size=4, max_size=4)

@register_model
class PictureChoiceLesson(models.Model):
    ns = _ns
    nsmap = {'picture_choice': ns}

    groups = models.ArrayElement(models.ResourceElement(PictureChoiceGroup))
