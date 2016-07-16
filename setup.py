# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='chakert',
    version='0.2',
    packages=['chakert',
              'chakert.langs'],
    requires=[
        'lxml',
    ],
    author='Harut Dagesian',
    author_email='yes@harutune.name',
    description='Typographer for lxml and plain text. '
                'Supports English and Russian languages.',
    #long_description=open('README').read(),
    url='http://github.com/Harut/chakert/',
    license='MIT',
    keywords='html lxml typography typographer typo',
)
