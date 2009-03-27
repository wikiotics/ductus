from ductus.resource import models, register_model
from ductus.modules.picture.models import Picture

class PictureChoice(models.Element):
    ns = 'http://wikiotics.org/ns/2009/picture_choice'
    nsmap = {'picture_choice': ns}

    phrase = models.TextElement()
    picture = models.ResourceElement(Picture)

class PictureChoiceGroup(models.Model):
    ns = 'http://wikiotics.org/ns/2009/picture_choice'

    group = models.ArrayElement(PictureChoice(), min_size=4, max_size=4)

register_model(PictureChoiceGroup)
