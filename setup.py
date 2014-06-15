# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='etree_typo',
    version='0.1',
    packages=['etree_typo',
              'etree_typo.langs'],
    requires=[
        'lxml',
    ],
    author='Harut Dagesian',
    author_email='yes@harutune.name',
    description='Typographer for lxml and plain text. '
                'Supports English and Russian languages.',
    #long_description=open('README').read(),
    url='http://github.com/Harut/etree_typo/',
    license='MIT',
    keywords='html lxml typography',
)
