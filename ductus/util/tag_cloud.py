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

class TagCloudElement(object):
    """An element that will be placed in a tag cloud
    """

    def __init__(self, weight, label=None, href=None, **kwargs):
        self.weight = weight
        if label is not None:
            self.label = label
        if href is not None:
            self.href = href
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class TagCloudElementProxy(object):
    """A proxy to a TagCloudElement, created when prepare_tag_cloud() is called

    This contains everything the original TagCloudElement contained, plus a
    field called "percent" representing the tag's size
    """

    __slots__ = ('_tag_cloud_element', 'percent')

    def __init__(self, tag_cloud_element, percent):
        self._tag_cloud_element = tag_cloud_element
        self.percent = percent

    def __getattr__(self, name):
        return getattr(self._tag_cloud_element, name)

def prepare_tag_cloud(element_list, min_percent=50, max_percent=100):
    """Modifies element_list to make it a tag cloud
    """
    assert all(isinstance(tce, TagCloudElement) for tce in element_list)
    if not element_list:
        return
    min_weight = min(tce.weight for tce in element_list)
    max_weight = max(tce.weight for tce in element_list)
    from math import log
    slope = (max_percent - min_percent) / (log(max_weight - min_weight + 1) or 1.0)
    tmplist = [TagCloudElementProxy(tce, (slope * log(tce.weight - min_weight + 1) + min_percent))
               for tce in element_list]
    del element_list[:]
    element_list.extend(tmplist)
