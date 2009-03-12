from ductus.resource import models, register_model

class PictureChoice(models.Model):
    ns = 'http://wikiotics.org/ns/2009/picture_choice'
    phrase = models.TextElement()
    correct_picture = models.ResourceElement()
    incorrect_pictures = models.ArrayElement(models.ResourceElement(),
                                             min_size=3, max_size=3)
register_model(PictureChoice)