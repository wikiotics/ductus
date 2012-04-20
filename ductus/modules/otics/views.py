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

from django.shortcuts import render_to_response
from django.template import RequestContext

from ductus.special.views import register_special_page
from ductus.util.bcp47 import language_tag_to_description
from ductus.util.tag_cloud import TagCloudElement, prepare_tag_cloud

@register_special_page
def front_page(request, pagename):
    # this is all temporarily hard-coded
    languages = (
        ('af', 1),
        ('ar', 1),
        ('bs', 1),
        ('ca', 1),
        ('zh', 5),
        ('nl', 1),
        ('en', 43),
        ('fi', 1),
        ('fr', 3),
        ('de', 1),
        ('el', 3),
        ('he', 1),
        ('hi', 1),
        ('is', 1),
        ('it', 1),
        ('ja', 1),
        ('ko', 1),
        ('no', 6),
        ('fa', 1),
        ('pt', 1),
        ('ru', 1),
        ('sk', 1),
        ('es', 5),
        ('sv', 1),
        ('tr', 1),
    )
    total_lesson_count = sum(a[1] for a in languages)
    language_tag_cloud = []
    for lang in languages:
        descr = language_tag_to_description(lang[0])
        if lang[0] == 'el':  # temporary (?) override
            descr = u'Greek'
        language_tag_cloud.append(TagCloudElement(lang[1], label=descr, href=(u"/en/%s_lessons" % descr), data=lang[0]))
    prepare_tag_cloud(language_tag_cloud, min_percent=70, max_percent=150)
    return render_to_response('otics/front_page.html', {
        'language_tag_cloud': language_tag_cloud,
        'total_lesson_count': total_lesson_count,
        'total_language_count': len(languages),
    }, RequestContext(request))
