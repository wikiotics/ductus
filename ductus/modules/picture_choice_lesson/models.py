from ductus.resource import models, register_model

class PictureChoiceLesson(models.Model):
    ns = 'http://wikiotics.org/ns/2009/picture_choice_lesson'
    questions = models.ArrayElement(models.ResourceElement())
register_model(PictureChoiceLesson)
