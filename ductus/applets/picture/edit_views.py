# Ductus
# Copyright (C) 2008  Jim Garrison <jim@garrison.cc>
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

# TODO: license saving
#       determine whether the default view should just show the image or license info too
#       which namespace to save license info in
#       what license info to save
#       intermediate "data model" class
#       allowed licenses

from django.http import HttpResponse
from ductus.apps.urn import get_resource_database
from ductus.util import iterate_file_object
from ductus.util.xml import add_simple_xlink, make_ns_func
from ductus.util.http import render_json_response

import re
from urllib2 import urlopen
from cStringIO import StringIO
from lxml import etree

nsmap = {
    None: 'http://wikiotics.org/ns/2008/picture',
    'xlink': 'http://www.w3.org/1999/xlink',
}
ns = make_ns_func(nsmap)

allowed_licenses = (
    'http://creativecommons.org/licenses/publicdomain/',
    'http://creativecommons.org/licenses/by-sa/1.0/',
    'http://creativecommons.org/licenses/by-sa/2.0/',
    'http://creativecommons.org/licenses/by-sa/2.5/',
    'http://creativecommons.org/licenses/by-sa/3.0/',
    'http://creativecommons.org/licenses/by/1.0/',
    'http://creativecommons.org/licenses/by/2.0/',
    'http://creativecommons.org/licenses/by/2.5/',
    'http://creativecommons.org/licenses/by/3.0/',
)
allowed_licenses = set(allowed_licenses)

base_url_re = re.compile(r'(http\://[A-Za-z\.]*flickr\.com/photos/[A-Za-z0-9_\-\.@]+/[0-9]+/)')
rdf_re = re.compile(r'(\<rdf\:RDF.*\</rdf\:RDF\>)', re.DOTALL)
huge_re = re.compile(r'(http\://farm.*?_o_d.jpg)')

def download_flickr(url):
    # verify it is a flickr url and modify url in whatever ways we
    # need ... make sure only allowed characters are there (what are
    # constraints on flickr username?)
    base_url = base_url_re.match(url).group(1)

    base_url_contents = urlopen(base_url).read()

    # use regular expressions to isolate the RDF document
    rdf_portion = rdf_re.search(base_url_contents).group(1)

    # parse RDF and get license information
    tree = etree.parse(StringIO(rdf_portion))
    root = tree.getroot()
    #return etree.tostring(tree.getroot())

    # find huge image
    huge_html_url = base_url + 'sizes/o/'
    huge_html_contents = urlopen(huge_html_url).read()
    huge_jpg_url = huge_re.search(huge_html_contents).group(1)

    # download and store image blob
    db = get_resource_database()
    blob_urn = db.store_blob(iterate_file_object(urlopen(huge_jpg_url)))

    # put together all picture info
    return {'license': root.find('.//{http://web.resource.org/cc/}license').get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'),
            'creator': root.findtext('.//{http://purl.org/dc/elements/1.1/}creator/{http://web.resource.org/cc/}Agent/{http://purl.org/dc/elements/1.1/}title'),
            'rights': root.findtext('.//{http://purl.org/dc/elements/1.1/}rights/{http://web.resource.org/cc/}Agent/{http://purl.org/dc/elements/1.1/}title'),
            'blob_urn': blob_urn,
            'original_url': base_url}

def save_picture(picture_info):
    if picture_info['license'] not in allowed_licenses:
        # fixme: fix string exception
        raise "License not allowed (%s)" % picture_info['license']

    # save authorship/copyright XML
    root = etree.Element(ns('picture'), nsmap=nsmap)
    blob = etree.SubElement(root, ns('blob'))
    add_simple_xlink(blob, picture_info['blob_urn'])
    blob.attrib[ns('type')] = 'image/jpeg'
    add_simple_xlink(etree.SubElement(root, ns('license')),
                     picture_info['license'])
    etree.SubElement(root, ns('creator')).text = picture_info['creator']
    etree.SubElement(root, ns('rights')).text = picture_info['rights']
    add_simple_xlink(etree.SubElement(root, ns('original_url')),
                     picture_info['original_url'])

    urn = get_resource_database().store_xml(etree.tostring(root))

    # save log of what we just did ?

    return urn

def new_picture(request):
    if request.method == 'POST':
        # TODO: plugin system to recognize URI style and fetch image
        uri = request.POST['uri']
        if uri.startswith('urn:'):
            urn = uri # fixme: we should verify it exists and is a picture!
        else:
            # could combine these lines into a single call
            picture_info = download_flickr(uri)
            urn = save_picture(picture_info)

        view = request.GET.get('view', None)
        if view == 'json':
            return render_json_response({'urn': urn})
        return HttpResponse(urn)

    else:
        return HttpResponse('<form method="post">Enter a URI: <input name="uri"/><input type="submit" /></form>')
