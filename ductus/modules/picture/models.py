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

@register_model
class Picture(models.Model):
    ns = 'http://wikiotics.org/ns/2009/picture'
    blob = models.TypedBlobElement(allowed_mime_types=['image/jpeg'])
    credit = CreditElement()
    rotation = models.Attribute(optional=True, blank_is_null=True,
                                validator=rotation_validator)

    def patch_from_blueprint(self, blueprint, save_context):
        models.blueprint_expects_dict(blueprint)
        blueprint = dict(blueprint)
        if "credit" in blueprint:
            del blueprint["credit"]

        super(Picture, self).patch_from_blueprint(blueprint, save_context)

        if 'flickr_photo_id' in blueprint:
            flickr_photo_id = blueprint['flickr_photo_id']
            flickr_photo_id = models.blueprint_cast_to_string(flickr_photo_id)
            # FIXME TEMPORARY
            from ductus.modules.picture.flickr import FlickrUriHandler
            url = 'http://flickr.com/photos/0/%s' % flickr_photo_id
            if FlickrUriHandler.handles(url):
                fuh = FlickrUriHandler(url)
                fuh.validate()
                fuh.save(self, return_before_saving=False)

        if 'rotation' in blueprint:
            rotation = blueprint['rotation']
            rotation = models.blueprint_cast_to_string(rotation)
            rotation_validator(rotation)
            self.rotation = rotation

        if 'net_rotation' in blueprint:
            net_rotation = blueprint['net_rotation']
            net_rotation = models.blueprint_cast_to_string(net_rotation)
            rotation_validator(net_rotation)
            self.rotation = str((int(self.rotation or 0) +
                                 int(net_rotation or 0)) % 360)
