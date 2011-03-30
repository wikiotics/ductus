# Ductus
# Copyright (C) 2011  Jim Garrison <garrison@wikiotics.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    # '' or None means follow EXIF metadata.  an explicit '0' overrides any
    # metadata and refuses to perform a rotation.
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
                fuh.save(save_context, picture=self, return_before_saving=True)

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
