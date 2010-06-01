#!/usr/bin/env python

# this file is likely to be out of date at any given time

# fixme: recursive-include's in MANIFEST.in don't ignore text editor backup
# files (such as *~)

# fixme: depend on Python >= 2.6 somehow

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Ductus',
    version='0.1pre',
    description='Structured wiki system, designed for language instruction at wikiotics.org',
    license='GNU GPLv3 or later',
    author='Jim Garrison',
    author_email='jim@garrison.cc',
    url='http://ductus.us/',
    install_requires=(
        'Django >= 1.2',
        'Creoleparser >= 0.7.2',
        'lxml',
        'PIL',
    ),
    extras_require={
        'flickr': ['flickrapi >= 1.2'],
        'highlighting': ['pygments'],
        'captcha': ['recaptcha-client'],
    },
    packages=(
        'ductus',
        'ductus.util',
        'ductus.resource',
        'ductus.resource.storage',
        'ductus.special',
        'ductus.wiki',
        'ductus.wiki.templatetags',
        'ductus.user',
        'ductus.template_loaders',
        'ductus.middleware',
        'ductus.license',
        'ductus.modules',
        'ductus.modules.picture',
        'ductus.modules.picture_choice',
        'ductus.modules.textwiki',
        'ductus.modules.textwiki.templatetags',
    ),
)
