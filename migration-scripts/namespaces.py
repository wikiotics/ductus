#!/usr/bin/env python

# This script was used to update the WikiPage names after commit
# 5fc694545542e345ea64f860d823caf719a280eb, which added namespaces

import ductus.initialize
from ductus.wiki.models import WikiPage

def map_func(name):
    if name == 'front_page':
        return 'en:main_page'
    if name.startswith('~'):
        return 'user/' + name[1:]
    if ':' not in name:
        return 'en:' + name
    return name

d = {
    '/wiki/+recent_changes': '/special/recent_changes',
}
for wikipage in WikiPage.objects.all():
    old_name = wikipage.name
    wikipage.name = map_func(old_name)
    d['/wiki/' + old_name] = '/' + wikipage.name.replace(':', '/', 1)
    wikipage.save()
print repr(d)
