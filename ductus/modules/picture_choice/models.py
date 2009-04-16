from ductus.resource import models, register_model
from ductus.modules.picture.models import Picture

_ns = 'http://wikiotics.org/ns/2009/picture_choice'

class PictureChoiceElement(models.Element):
    ns = _ns
    nsmap = {'picture_choice': ns}

    phrase = models.TextElement()
    picture = models.ResourceElement(Picture)

class PictureChoiceGroup(models.Model):
    ns = _ns
    nsmap = {'picture_choice': ns}

    group = models.ArrayElement(PictureChoiceElement(), min_size=4, max_size=4)

register_model(PictureChoiceGroup)

class PictureChoiceLesson(models.Model):
    ns = _ns
    nsmap = {'picture_choice': ns}

    groups = models.ArrayElement(models.ResourceElement(PictureChoiceGroup))

register_model(PictureChoiceLesson)
