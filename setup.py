# -*- coding: utf-8 -*-

from distutils.core import setup

extras_requires = {
    'html': ['lxml'],
}

setup(
    name='chakert',
    version='0.2.1',
    packages=['chakert',
              'chakert.langs'],
    extras_require=extras_requires,
    author='Harut Dagesian',
    author_email='yes@harutune.name',
    description='Typographer for lxml and plain text. '
                'Supports English and Russian languages.',
    #long_description=open('README').read(),
    url='http://github.com/Harut/chakert/',
    license='MIT',
    keywords='html lxml typography typographer typo',
)
