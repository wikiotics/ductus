#!/usr/bin/env python

# this file is likely to be out of date at any given time

# fixme: recursive-include's in MANIFEST.in don't ignore text editor backup
# files (such as *~)

# fixme: depend on Python >= 2.5 somehow

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Ductus',
    version='0.1pre',
    description='Wikiotics wiki system',
    license='GNU GPLv3 or later',
    author='Jim Garrison',
    author_email='jim@garrison.cc',
    url='http://wikiotics.org/',
    install_requires=(
        'Django >= 1.0',
        'Creoleparser',
    ),
    extras_require={
        'flickr': ['flickrapi >= 1.2'],
        'highlighting': ['pygments'],
    },
    packages=(
        'ductus',
        'ductus.util',
        'ductus.resource',
        'ductus.resource.storage',
        'ductus.wiki',
        'ductus.user',
        'ductus.template_loaders',
        'ductus.middleware',
        'ductus.applets',
        'ductus.applets.picture',
        'ductus.applets.picture_choice',
        'ductus.applets.picture_choice_lesson',
        'ductus.applets.textwiki',
        'ductus.applets.textwiki.templatetags',
    ),
)
