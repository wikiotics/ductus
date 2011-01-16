# Ductus
# Copyright (C) 2009  Jim Garrison <jim@garrison.cc>
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

import re
import copy
import datetime
from itertools import chain

from lxml import etree

from django.conf import settings
from django.utils.datastructures import SortedDict

from ductus.license import is_license_compatibility_satisfied
from ductus.util import create_property
from ductus.resource import register_model, get_resource_database, _registered_models

# fixme: we could just not "follow" parents instead of excluding them.  If we
# change it to work this way, the browser will be aware of the parents in case
# that's ever necessary.  Plus, there may be other things we don't want to
# follow (but I can't think of any right now).

class ValidationError(Exception):
    pass

class ModelMismatchError(Exception):
    pass

class BlueprintError(Exception):
    def __init__(self, value, blueprint):
        self.value = value
        self.blueprint = blueprint

    def __str__(self):
        import json
        return u'%s -- %s' % (repr(self.value), json.dumps(self.blueprint))

class BlueprintTypeError(BlueprintError):
    pass

def allowed_values_attribute_validator(allowed_values):
    def validator(v):
        if v not in allowed_values:
            raise ValidationError
    return validator

def camelcase_to_underscores(v):
    # re lifted from django.db.models.options
    return re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', ' \\1', v).lower().strip().replace(' ', '_')

def oldest_ancestor(x):
    while True:
        x, y = getattr(x, "_parent", None), x
        if x is None:
            return y

def _is_element(obj):
    "This function gets overwritten below once Element is defined"
    return False

class ElementMetaclass(type):
    def __init__(cls, name, bases, attrs):
        # Set up attributes
        def attribute_property(name, obj):
            def fget(s):
                return s._attribute_data[name]
            def fset(s, v):
                if not isinstance(v, basestring):
                    raise ValidationError
                obj.validate(v)
                s._attribute_data[name] = v
            if obj.optional:
                def fdel(s):
                    s._attribute_data[name] = None
            else:
                fdel = None
            return property(fget, fset, fdel, obj.__doc__)
        attributes = dict(a for a in attrs.items() if isinstance(a[1], Attribute))
        for a, o in attributes.items():
            setattr(cls, a, attribute_property(a, o))
        cls.attributes = {}
        for base in reversed(bases):
            if hasattr(base, "attributes"):
                cls.attributes.update(base.attributes)
        cls.attributes.update(attributes)

        # Set up subelements
        subelements = [s for s in attrs.items() if _is_element(s[1])]
        subelements.sort(key=lambda s: s[1].creation_counter)
        subelements = SortedDict(subelements)
        for subelement in subelements:
            delattr(cls, subelement)
        cls.subelements = SortedDict()
        for base in reversed(bases):
            if hasattr(base, "subelements"):
                cls.subelements.update(base.subelements)
        cls.subelements.update(subelements)

        super(ElementMetaclass, cls).__init__(name, bases, attrs)

class NoChildElementMetaclass(ElementMetaclass):
    "Forbids subelements (but allows attributes)"
    def __init__(cls, name, bases, attrs):
        super(NoChildElementMetaclass, cls).__init__(name, bases, attrs)
        if cls.subelements:
            raise Exception("%s does not allow subelements" % cls.__name__)

class ModelMetaclass(ElementMetaclass):
    def __init__(cls, name, bases, attrs):
        super(ModelMetaclass, cls).__init__(name, bases, attrs)
        if name == "Model":
            return

        # Deal with root_name, fqn
        if 'root_name' not in attrs:
            cls.root_name = camelcase_to_underscores(name)
        cls.fqn = '{%s}%s' % (cls.ns, cls.root_name)

        # Create nsmap
        nsmap = {}
        def add_nsmap_of_descendants(element_class):
            children = element_class.subelements.values()
            children += [subelement.item_prototype for subelement in children
                         if isinstance(subelement, ArrayElement)]
            for subelement in children:
                add_nsmap_of_descendants(subelement.__class__)
            children += element_class.attributes.values()
            nsmaps = [obj.nsmap for obj in children if hasattr(obj, "nsmap")]
            nsmaps = dict([(y, x) for (x, y) in chain(*[nsm.items() for nsm in nsmaps]) if y != cls.ns])
            nsmap.update(dict([(y, x) for (x, y) in nsmaps.items()]))
        add_nsmap_of_descendants(cls)
        nsmap[None] = cls.ns
        cls.nsmap = nsmap

class Attribute(object):
    def __init__(self, optional=False, validator=None, fqn=None, blank_is_null=True):
        self.optional = optional
        self.validator = validator
        self.fqn = fqn
        self.blank_is_null = blank_is_null

    def validate(self, v):
        if self.validator:
            self.validator(v)

class Element(object):
    __metaclass__ = ElementMetaclass
    creation_counter = 0
    fqn = None
    ns = None

    def __init__(self):
        self._attribute_data = dict((a, None if o.optional else "") for a, o in self.attributes.items())
        for name, subelement in self.subelements.items():
            setattr(self, name, subelement.clone())
        self.creation_counter = Element.creation_counter
        Element.creation_counter += 1

    def clone(self):
        clone = copy.copy(self)
        clone._attribute_data = dict(self._attribute_data)
        for name in self.subelements:
            setattr(clone, name, getattr(self, name).clone())
        clone._parent = self
        return clone

    def output_json_dict(self, exclude=()):
        rv = {}
        # figure out how we are going to override things
        # what the heck did i mean by override things?
        # we should probably just output the blank string for null attributes, output null elements, etc
        for name, subelement in self.subelements.items():
            # fixme: should we really be testing is_null_xml_element here?
            if not getattr(self, name).is_null_xml_element() and not name in exclude:
                rv[name] = getattr(self, name).output_json_dict()
        for name, attribute in self.attributes.items():
            if not (attribute.optional and attribute.blank_is_null and not self._attribute_data[name]):
                rv[name] = self._attribute_data[name]
        return rv

    def patch_from_blueprint(self, blueprint, save_context):
        blueprint_expects_dict(blueprint)

        blueprint_set = set(blueprint)
        attribute_name_set = set(self.attributes.keys())
        subelement_name_set = set(self.subelements.keys())

        # patch all attributes
        for attribute_name in (blueprint_set & attribute_name_set):
            attribute_blueprint = blueprint[attribute_name]
            attribute_blueprint = blueprint_cast_to_string(attribute_blueprint)
            setattr(self, attribute_name, attribute_blueprint)

        # patch all subelements
        for subelement_name in (blueprint_set & subelement_name_set):
            subelement = getattr(self, subelement_name)
            subelement.patch_from_blueprint(blueprint[subelement_name], save_context)

    def populate_xml_element(self, element, ns):
        for name, subelement in self.subelements.items():
            if not getattr(self, name).is_null_xml_element():
                local_ns = subelement.ns or ns
                fqn = subelement.fqn or "{%s}%s" % (local_ns, name)
                xml_subelement = etree.SubElement(element, fqn)
                getattr(self, name).populate_xml_element(xml_subelement, local_ns)
        for name, attribute in self.attributes.items():
            fqn = attribute.fqn or name
            if not (attribute.optional and attribute.blank_is_null and not self._attribute_data[name]):
                element.set(fqn, self._attribute_data[name])

    def is_null_xml_element(self):
        return False

    def populate_from_xml(self, xml_node, ns=None):
        if ns is None:
            # we must be a Model
            ns = self.ns
        self._populate_subelements_from_xml(xml_node, ns)
        self._populate_attributes_from_xml(xml_node, ns)

    def _populate_subelements_from_xml(self, xml_node, ns):
        used_tags = set()
        subelements_by_fqn = {}
        for name, subelement in self.subelements.items():
            fqn = subelement.fqn or "{%s}%s" % (subelement.ns or ns, name)
            subelements_by_fqn[fqn] = getattr(self, name)
        for child in xml_node:
            if child.tag in used_tags:
                raise Exception("Each tag must be unique")
            used_tags.add(child.tag)
            try:
                subelement = subelements_by_fqn[child.tag]
            except KeyError:
                raise Exception("Unrecognized tag")
            subelement.populate_from_xml(child, subelement.ns or ns)
        required_tags = set(fqn for fqn, subelement in subelements_by_fqn.items()
                            if not getattr(subelement, "optional", False))
        missing_tags = required_tags.difference(used_tags)
        if missing_tags:
            raise Exception("Missing tag(s)! %s" % tuple(missing_tags))

    def _populate_attributes_from_xml(self, xml_node, ns):
        used_attributes = set()
        attributes_by_fqn = {}
        for name, attribute in self.attributes.items():
            fqn = attribute.fqn or name
            attributes_by_fqn[fqn] = name
        for attr, value in xml_node.attrib.items():
            used_attributes.add(attr)
            try:
                name = attributes_by_fqn[attr]
            except KeyError:
                raise Exception("Unrecognized attribute tag: %s" % attr)
            setattr(self, name, value)
        required_attributes = set(fqn for fqn, name in attributes_by_fqn.items()
                                  if not getattr(self.attributes[name], "optional", False))
        missing_attributes = required_attributes.difference(used_attributes)
        if missing_attributes:
            raise Exception("Missing attribute(s)! %s" % tuple(missing_attributes))

    def validate(self, strict=True):
        for name, subelement in self.subelements.items():
            obj = getattr(self, name)
            # verify that the object is in fact a subelement of acceptable lineage
            if oldest_ancestor(self.subelements[name]) is not oldest_ancestor(obj):
                # fixme: if we are looking at a string, give an appropriate
                # error message (it is quite easy to accidentally set a
                # TextElement itself instead of its text property)
                raise ValidationError
            # validate it
            obj.validate(strict)
        for name, attribute in self.attributes.items():
            attribute.validate(self._attribute_data[name])

    def __eq__(self, other):
        if self is other:
            return True
        return (type(self) == type(other) and
                self._attribute_data == other._attribute_data and
                all(getattr(self, name) == getattr(other, name) for name in self.subelements))

    def __ne__(self, other):
        return not self.__eq__(other)

def _is_element(obj):
    return isinstance(obj, Element)

class TextElement(Element):
    __metaclass__ = NoChildElementMetaclass
    _text = ""

    # fixme: In theory we should prevent subclasses from having adding elements
    # or attributes named "text"

    @create_property
    def text():
        def fget(self):
            return self._text
        def fset(self, v):
            if not isinstance(v, basestring):
                raise TypeError
            self._text = v
        def fdel(self):
            self._text = ""
        doc = "Textual contents of the element"
        return locals()

    def populate_xml_element(self, element, ns):
        super(TextElement, self).populate_xml_element(element, ns)
        element.text = self.text

    def populate_from_xml(self, xml_node, ns):
        super(TextElement, self).populate_from_xml(xml_node, ns)
        text = xml_node.text
        if text is None:
            text = ""
        self.text = text

    def __eq__(self, other):
        return super(TextElement, self).__eq__(other) and self._text == other._text

    def output_json_dict(self):
        rv = super(TextElement, self).output_json_dict()
        rv['text'] = self.text
        return rv

    def patch_from_blueprint(self, blueprint, save_context):
        super(TextElement, self).patch_from_blueprint(blueprint, save_context)
        if 'text' in blueprint:
            text = blueprint['text']
            blueprint_expects_string(text)
            self.text = text

class ArrayElement(Element):
    __metaclass__ = NoChildElementMetaclass

    # fixme: In theory we should prevent subclasses from having adding elements
    # or attributes named "array"

    def __init__(self, item_prototype, min_size=0, max_size=None, null_on_empty=False):
        super(ArrayElement, self).__init__()
        assert max_size is None or min_size <= max_size
        assert isinstance(item_prototype, Element)
        self.item_prototype = item_prototype
        self.min_size = min_size
        self.max_size = max_size
        self.null_on_empty = null_on_empty
        self.array = []

    @property
    def optional(self):
        return self.null_on_empty

    def clone(self):
        clone = super(ArrayElement, self).clone()
        clone.array = list(self.array)
        return clone

    def is_null_xml_element(self):
        return (self.null_on_empty and len(self.array) == 0)

    def new_item(self):
        return self.item_prototype.clone()

    def validate(self, strict=True):
        super(ArrayElement, self).validate(strict)
        prototype_oldest_ancestor = oldest_ancestor(self.item_prototype)
        if any(oldest_ancestor(item) is not prototype_oldest_ancestor for item in self.array):
            raise ValidationError
        if len(self) < self.min_size:
            raise ValidationError("too few elements")
        if self.max_size is not None and len(self) > self.max_size:
            raise ValidationError("too many elements")
        for subelement in self.array:
            subelement.validate(strict)

    def output_json_dict(self):
        rv = super(ArrayElement, self).output_json_dict()
        rv['array'] = [x.output_json_dict() for x in self.array]
        return rv

    def patch_from_blueprint(self, blueprint, save_context):
        super(ArrayElement, self).patch_from_blueprint(blueprint, save_context)
        if 'array' in blueprint:
            array_blueprint = blueprint['array']
            blueprint_expects_list(array_blueprint)
            self.array = [self.new_item() for a in array_blueprint]
            for i, bp in enumerate(array_blueprint):
                self.array[i].patch_from_blueprint(bp, save_context)

    def populate_xml_element(self, element, ns):
        super(ArrayElement, self).populate_xml_element(element, ns)
        for subelement in self.array:
            child_fqn = subelement.fqn or "{%s}%s" % (ns, "item") # fixme: "item"
            xml_subelement = etree.SubElement(element, child_fqn)
            subelement.populate_xml_element(xml_subelement, ns)

    def populate_from_xml(self, xml_node, ns):
        super(ArrayElement, self)._populate_attributes_from_xml(xml_node, ns) # or we can just forbid arrays from having attributes
        for child in xml_node:
            # fixme: make sure child.tag is as expected (see "item" above)
            item = self.new_item()
            item.populate_from_xml(child, ns)
            self.array.append(item)

    def __eq__(self, other):
        return super(ArrayElement, self).__eq__(other) and self.array == other.array

    def __iter__(self):
        return iter(self.array)

    def __len__(self):
        return len(self.array)

    # fixme: __getitem__, __delitem__, __setitem__, __delslice__, __getslice__,
    # __setslice__, __reversed__, append, extend, insert, pop

    # maybe make an interface for new_item to be passed arguments, which will
    # call some yet-to-be-defined "set_stuff" function on the item

class LinkElement(Element):
    nsmap = {"xlink": "http://www.w3.org/1999/xlink"}

    href = Attribute(fqn="{http://www.w3.org/1999/xlink}href")
    _xlink_type = Attribute(fqn="{http://www.w3.org/1999/xlink}type",
                            validator=allowed_values_attribute_validator(("simple",)))

    def __init__(self):
        super(LinkElement, self).__init__()
        self._xlink_type = "simple"

    def output_json_dict(self):
        rv = super(LinkElement, self).output_json_dict()
        del rv['_xlink_type']
        return rv

class LicenseElement(LinkElement):
    pass
    #or_later = BooleanAttribute(optional=True, default=False)

class ResourceElement(LinkElement):
    "Verify it is a URN that exists in our universe (whatever that means)"

    # fixme: In theory we should prevent subclasses from having adding elements
    # or attributes named "resource"

    def __init__(self, *allowed_resource_types):
        # fixme: should be able to specify more general constraints on allowed
        # resource types
        # fixme: or should we instead allow only one resource type (an
        # "interface" and force things to derive from it?)
        self.allowed_resource_types = allowed_resource_types
        super(ResourceElement, self).__init__()

    def store(self, resource):
        self.__check_type(resource)
        self.href = resource.save()

    def get(self):
        if self.href == "":
            return None
        if hasattr(self, "_cached_resource") and self._cached_resource[0] == self.href:
            return self._cached_resource[1]
        resource = get_resource_database().get_resource_object(self.href)
        self.__check_type(resource)
        self._cached_resource = (self.href, resource)
        return resource

    #resource = property(get, store)

    def validate(self, strict=True):
        super(ResourceElement, self).validate(strict)
        if strict and self.href:
            resource = get_resource_database().get_resource_object(self.href)
            self.__check_type(resource)

    def __check_type(self, resource):
        if self.allowed_resource_types:
            if not type(resource) in self.allowed_resource_types:
                raise Exception("Not a correct resource type")

    def output_json_dict(self):
        rv = super(ResourceElement, self).output_json_dict()
        resource = self.get()
        rv['resource'] = resource and resource.output_json_dict()
        return rv

    def patch_from_blueprint(self, blueprint, save_context):
        super(ResourceElement, self).patch_from_blueprint(blueprint, save_context)
        if 'resource' in blueprint:
            if blueprint['resource'] is None:
                # (it's possible to remove reference to the resource by setting
                # href to the empty string, but we support setting the resource
                # to null as well)
                self.href = None
            else:
                self.href = Model.save_blueprint({
                    'resource': blueprint['resource']
                }, save_context)

class BlobElement(LinkElement):
    "Verify it is a blob" # (fixme)

    def store(self, iterable):
        self.href = get_resource_database().store_blob(iterable)

    def __iter__(self):
        if self.href:
            return get_resource_database().get_blob(self.href)
        else:
            return ()

class TypedBlobElement(BlobElement):
    "Add type attribute"

    mime_type = Attribute()

    def __init__(self, allowed_mime_types=None):
        super(TypedBlobElement, self).__init__()
        if allowed_mime_types is not None:
            allowed_mime_types = frozenset(allowed_mime_types)
        self.allowed_mime_types = allowed_mime_types

    def validate(self, strict=True):
        super(TypedBlobElement, self).validate(strict)
        if self.mime_type not in self.allowed_mime_types:
            raise ValidationError("not an allowed mime type")

class TextBlobElement(BlobElement):
    # fixme: textual diff
    pass

class _AuthorElement(LinkElement, TextElement):
    pass

class DuctusCommonElement(Element):
    author = _AuthorElement()
    parents = ArrayElement(ResourceElement())
    licenses = ArrayElement(LicenseElement(), null_on_empty=True)
    timestamp = Attribute()
    log_message = TextElement()

    # rejected: title, languages, source url

    ns = "http://ductus.us/ns/2009/ductus"
    nsmap = {"ductus": ns}

    def clone(self):
        rv = super(DuctusCommonElement, self).clone()
        rv.parents.array = []
        rv.timestamp = ""
        rv.log_message.text = ""
        rv.author.text = ""
        rv.author.href = ""
        return rv

    def validate(self, strict=True):
        super(DuctusCommonElement, self).validate(strict)

        if strict:
            if not self.author.text:
                raise ValidationError("author must be given for the resource")

            # load each parent; make sure license compatibility is satisfied.
            licenses = [license.href for license in self.licenses]
            for parent in self.parents:
                parent_licenses = [license.href
                                   for license in parent.get().common.licenses]

                if not is_license_compatibility_satisfied(parent_licenses, licenses):
                    raise ValidationError("license compatibility not satisfied")

    def populate_xml_element(self, element, ns):
        if not self.timestamp:
            self.timestamp = datetime.datetime.utcnow().isoformat()
        super(DuctusCommonElement, self).populate_xml_element(element, ns)

    def output_json_dict(self):
        return Element.output_json_dict(self, ('parents',))

    def patch_from_blueprint(self, blueprint, save_context):
        # we don't allow patching, so we don't call the superclass
        self.author.text = save_context.author_username or save_context.author_ip_address
        self.author.href = save_context.author_full_absolute_url
        self.log_message.text = save_context.log_message

class Model(Element):
    __metaclass__ = ModelMetaclass

    urn = None
    common = DuctusCommonElement()

    __allowed_licenses_set = set(settings.DUCTUS_ALLOWED_LICENSES)

    def save(self, encoding=None):
        if self.urn:
            return self.urn # no-op

        # for now, let's just set the license to cc-by-sa if one isn't
        # explicitly given:
        if not self.common.licenses.array:
            self.common.licenses.array = [self.common.licenses.new_item()]
            self.common.licenses.array[0].href = settings.DUCTUS_DEFAULT_LICENSE

        self.validate()
        root = etree.Element(self.fqn, nsmap=self.nsmap)
        self.populate_xml_element(root, self.ns)
        resource_database = get_resource_database()
        self.urn = resource_database.store_xml_tree(root, encoding=encoding)
        return self.urn

    @classmethod
    def load(cls, urn):
        resource = get_resource_database().get_resource_object(urn)
        if type(resource) != cls:
            raise ModelMismatchError("Expecting %s, got %s" % (cls, type(resource)))
        return resource

    def clone(self):
        rv = super(Model, self).clone()
        rv.urn = None
        if self.urn:
            rv.common.parents.array = [rv.common.parents.new_item()]
            rv.common.parents.array[0].href = self.urn
        return rv

    def validate(self, strict=True):
        """validate the in-memory data model

        `strict` is occasionally False, such as when an existing resource from
        the ResourceDatabase is loaded into memory.  In this case, we don't
        want to waste our time checking that all linked resources are of the
        correct type (as this would involve loading them, and so on), so we
        just do the minimal checks available with what is in memory.

        Also, it is possible to implement a test that is performed only when
        strict=True.  This will allow the test to fail without complaint on any
        existing resources, but the system will only save new resources if they
        pass the test.
        """
        super(Model, self).validate(strict)
        if strict:
            for parent in self.common.parents:
                if type(parent.get()) != type(self):
                    raise ValidationError("Resource's parents must be of the same type")

        licenses = [license.href for license in self.common.licenses]
        if self.__allowed_licenses_set.isdisjoint(licenses + [None]):
            raise ValidationError("The content is not provided under a license acceptable for this wiki")

    def __eq__(self, other):
        return (self.urn is not None and self.urn == other.urn) or super(Model, self).__eq__(other)

    @classmethod
    def save_blueprint(cls, blueprint, save_context):
        """`blueprint` is a json object. Returns a URN"""
        # fixme: make sure the end result is compatible with the class.  this
        # might actually be easy if we just make sure the @constructor will
        # make a class we want, but this would eliminate our ability to make a
        # @constructor that outputs a resource of some type that is unknown
        # before its construction

        resource_database = get_resource_database()

        blueprint_expects_dict(blueprint)

        if 'href' in blueprint:
            href = blueprint['href']
            blueprint_expects_string(href)
            # we ensure it exists and is not a blob, then return the urn
            resource_database.get_xml(href)
            return href

        try:
            resource_blueprint = blueprint['resource']
        except KeyError:
            raise BlueprintError("blueprint needs either `href` or `resource`", blueprint)
        blueprint_expects_dict(resource_blueprint)
        resource_blueprint = dict(resource_blueprint) # copy it so we can modify

        if '@patch' in resource_blueprint:
            original_urn = resource_blueprint.pop('@patch')
            resource = resource_database.get_resource_object(original_urn).clone()
        elif '@create' in resource_blueprint:
            fqn = resource_blueprint.pop('@create')
            try:
                resource_class = _registered_models[fqn]
            except KeyError:
                raise BlueprintError("invalid argument to `@create`", resource_blueprint)
            if not issubclass(resource_class, cls):
                raise BlueprintError("resource is not of an acceptable model type", resource_blueprint)
            resource = resource_class()
        else:
            raise BlueprintError("resource blueprint must contain '@patch' or '@create'", resource_blueprint)

        resource.patch_from_blueprint(resource_blueprint, save_context)
        resource.common.patch_from_blueprint(None, save_context)
        return resource.save()

def blueprint_expects_dict(blueprint):
    if not isinstance(blueprint, dict):
        raise BlueprintTypeError("expected dict, got %s" % type(blueprint), blueprint)
    return blueprint

def blueprint_expects_list(blueprint):
    if not isinstance(blueprint, list):
        raise BlueprintTypeError("expected list, got %s" % type(blueprint), blueprint)
    return blueprint

def blueprint_expects_string(blueprint):
    if not isinstance(blueprint, basestring):
        raise BlueprintTypeError("expected string, got %s" % type(blueprint), blueprint)
    return blueprint

def blueprint_cast_to_string(blueprint):
    if isinstance(blueprint, basestring):
        return blueprint
    if isinstance(blueprint, int):
        return u'%d' % blueprint
    raise BlueprintTypeError("expected string, got %s" % type(blueprint), blueprint)

class BlueprintSaveContext(object):
    author_username = ""
    author_full_absolute_url = ""
    author_ip_address = ""
    log_message = ""

    @classmethod
    def from_request(cls, request):
        rv = cls()
        if request.user.is_authenticated():
            rv.author_username = request.user.username
            if getattr(settings, "DUCTUS_SITE_DOMAIN", None):
                rv.author_full_absolute_url = 'http://%s%s' % (settings.DUCTUS_SITE_DOMAIN, request.user.get_absolute_url())
        rv.author_ip_address = request.remote_addr
        rv.log_message = request.POST.get('log_message', '')
        return rv
