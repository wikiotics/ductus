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
from django.utils.datastructures import SortedDict
from ductus.util import create_property

class ValidationError(Exception):
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

class NoChildMetaclass(ElementMetaclass):
    "Forbids subelements (but allowed attributes)"
    def __init__(cls, name, bases, attrs):
        super(NoChildMetaclass, cls).__init__(name, bases, attrs)
        if cls.subelements:
            raise Exception("Subelements not allowed in a text element")

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
            for subelement in element_class.subelements.values():
                add_nsmap_of_descendants(subelement.__class__)
            children = element_class.attributes.values() + element_class.subelements.values()
            nsmaps = [obj.nsmap for obj in children if hasattr(obj, "nsmap")]
            nsmaps = dict([(y, x) for (x, y) in chain(*[nsm.items() for nsm in nsmaps])])
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

    def populate_xml_element(self, element, ns):
        for name, subelement in self.subelements.items():
            if not subelement.is_null_xml_element():
                fqn = subelement.fqn or "{%s}%s" % (ns, name)
                xml_subelement = etree.SubElement(element, fqn)
                getattr(self, name).populate_xml_element(xml_subelement, ns)
        for name, attribute in self.attributes.items():
            fqn = attribute.fqn or "{%s}%s" % (ns, name)
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
            fqn = subelement.fqn or "{%s}%s" % (ns, name)
            subelements_by_fqn[fqn] = getattr(self, name)
        for child in xml_node:
            if child.tag in used_tags:
                raise Exception("Each tag must be unique")
            used_tags.add(child.tag)
            try:
                subelement = subelements_by_fqn[child.tag]
            except KeyError:
                raise Exception("Unrecognized tag")
            subelement.populate_from_xml(child, ns)
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
        required_attributes = set(fqn for fqn, attr in attributes_by_fqn.items()
                                  if not getattr(attr, "optional", False))
        missing_attributes = required_attributes.difference(used_attributes)
        if missing_attributes:
            raise Exception("Missing attribute(s)! %s" % tuple(missing_attributes))

    def validate(self):
        for name, subelement in self.subelements.items():
            obj = getattr(self, name)
            # verify that the object is in fact a subelement of acceptable lineage
            if oldest_ancestor(self.subelements[name]) != oldest_ancestor(obj):
                raise ValidationError
            # validate it
            obj.validate()
        for name, attribute in self.attributes.items():
            attribute.validate(self._attribute_data[name])

def _is_element(obj):
    return isinstance(obj, Element)

class TextElement(Element):
    __metaclass__ = NoChildMetaclass
    _text = ""

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
        element.text = self._text

    def populate_from_xml(self, xml_node, ns):
        super(TextElement, self).populate_from_xml(xml_node, ns)
        text = xml_node.text
        if text is None:
            text = ""
        self.text = text

class ArrayElement(Element): # fixme: needs much work, especially XML work!
    __metaclass__ = NoChildMetaclass

    def __init__(self, item_prototype, min_size=0, max_size=None, null_on_empty=False):
        super(ArrayElement, self).__init__()
        assert max_size is None or min_size <= max_size
        assert isinstance(item_prototype, Element)
        self.item_prototype = item_prototype
        self.min_size = min_size
        self.max_size = max_size
        self.null_on_empty = null_on_empty # this doesn't really seem like essential functionality
        self.array = []

    def is_null_xml_element(self):
        return (self.null_on_empty and len(self.array) == 0)

    def new_item(self):
        return self.item_prototype.clone()

    def validate(self):
        super(ArrayElement, self).validate()
        prototype_oldest_ancestor = oldest_ancestor(self.item_prototype)
        if any(oldest_ancestor(item) != prototype_oldest_ancestor for item in self.array):
            raise ValidationError
        if len(self) < self.min_size:
            raise ValidationError("too few elements")
        if self.max_size is not None and len(self) > self.max_size:
            raise ValidationError("too many elements")

    def populate_xml_element(self, element, ns):
        super(ArrayElement, self).populate_xml_element(element, ns)
        for subelement in self.array:
            child_fqn = subelement.fqn or "{%s}%s" % (ns, "item") # fixme: "item"
            xml_subelement = etree.SubElement(element, child_fqn)
            subelement.populate_xml_element(xml_subelement, ns)

    def populate_from_xml(self, xml_node, ns):
        super(ArrayElement, self)._populate_attributes_from_xml(xml_node, ns) # or we can just forbid arrays from having attributes
        # fixme: do something!

    def __iter__(self):
        return iter(self.array)

    def __len__(self):
        return len(self.array)

    # fixme: __getitem__, __delitem__, __setitem__, __delslice__, __getslice__,
    # __setslice__, __eq__, __ne__, __reversed__, append, extend, insert, pop

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

class LicenseElement(LinkElement):
    pass
    #or_later = BooleanElement(optional=True, default=False)

class ResourceElement(LinkElement):
    "Verify it is a URN that exists in our universe (whatever that means)"

class BlobElement(ResourceElement):
    "Verify it is a blob"

    def iterate(self, resource_database=None):
        if self.href:
            return resource_database.get_blob(self.href)
        else:
            return ('',)

class TypedBlobElement(BlobElement):
    "Add type attribute"

    mime_type = Attribute()

    def __init__(self, allowed_mime_types=None):
        super(TypedBlobElement, self).__init__()
        if allowed_mime_types is not None:
            allowed_mime_types = frozenset(allowed_mime_types)
        self.allowed_mime_types = allowed_mime_types

    def validate(self):
        super(TypedBlobElement, self).validate()
        if self.mime_type not in self.allowed_mime_types:
            raise ValidationError()

class TimestampElement(TextElement): # maybe this should be an attribute
    pass

class DuctusCommonElement(Element):
    #title
    parents = ArrayElement(ResourceElement()) # do we allow URLs too?
    licenses = ArrayElement(LicenseElement()) #, optional=True) # null on empty
    timestamp = Attribute()
    #languages
    #author, rights, creator
    #source url (optional)
    log_message = TextElement()

    ns = "http://ductus.us/ns/2009/ductus"
    nsmap = {"ductus": ns}
    fqn = "{%s}common" % ns

    def clone(self):
        rv = super(DuctusCommonElement, self).clone()
        rv.parents.array = []
        rv.timestamp = ""
        rv.log_message.text = ""
        return rv

    def populate_xml_element(self, element, ns):
        if not self.timestamp:
            self.timestamp = datetime.datetime.utcnow().isoformat()
        super(DuctusCommonElement, self).populate_xml_element(element, ns)

class Model(Element):
    __metaclass__ = ModelMetaclass

    urn = None
    resource_database = None
    common = DuctusCommonElement()

    def save(self, resource_database=None, encoding=None):
        if self.urn:
            return self.urn # no-op
        resource_database = resource_database or self.resource_database
        assert resource_database is not None
        self.validate()
        root = etree.Element(self.fqn, nsmap=self.nsmap)
        self.populate_xml_element(root, self.ns)
        self.urn = resource_database.store_xml_tree(root, encoding=encoding)
        return self.urn

    def clone(self):
        rv = super(Model, self).clone()
        rv.urn = None
        # fixme: i really wish we could do this in DuctusCommonElement
#        rv.parents.array = [rv.parents.new_item(self)] # fixme
        if self.urn:
            rv.common.parents.array = [rv.common.parents.new_item()] # fixme
            rv.common.parents.array[0].href = self.urn
        return rv

from ductus.resource import register_model
