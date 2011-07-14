#!/usr/bin/env python

# If you find that Ductus fails to work with a setup that is valid according to
# the requirements given below, please report a bug at
# <http://code.ductus.us/>.  See also requirements.txt, which lists the
# specific packages this version of Ductus has been tested against.

# Python >= 2.6 (< 3.0) is also a dependency.

# fixme: recursive-include's in MANIFEST.in don't ignore text editor backup
# files (such as *~)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Ductus',
    version='0.2pre',
    description='Structured wiki system, designed for language instruction at wikiotics.org',
    license='GNU GPLv3 or later',
    author='Jim Garrison',
    author_email='garrison@wikiotics.org',
    url='http://ductus.us/',
    install_requires=(
        'Django >= 1.2',
        'Creoleparser >= 0.7.3',
        'lxml',
        'PIL',
        'python-magic',
    ),
    extras_require={
        'flickr': ['flickrapi >= 1.2'],
        'highlighting': ['pygments'],
        'captcha': ['recaptcha-client'],
    },
    packages=(
        'ductus',
        'ductus.initialize',
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
        'ductus.modules.audio',
        'ductus.modules.picture',
        'ductus.modules.picture_choice',
        'ductus.modules.textwiki',
        'ductus.modules.textwiki.templatetags',
    ),
)
