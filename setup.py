# -*- encoding: utf8 -*-
import os
import json
import codecs
from setuptools import setup, find_packages


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
version_info = json.load(open(os.path.join(BASE_DIR, 'scihub', 'version', 'version.json')))


setup(
    name='sci-hub',
    version=version_info['version'],
    author=version_info['author'],
    author_email=version_info['author_email'],
    description=version_info['desc'],
    long_description=codecs.open(os.path.join(BASE_DIR, 'README.md'), encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/suqingdong/scihub',
    project_urls={
        'Documentation': 'https://scihub.readthedocs.io',
        'Tracker': 'https://github.com/suqingdong/scihub/issues',
    },
    license='BSD License',
    install_requires=codecs.open(os.path.join(BASE_DIR, 'requirements.txt'), encoding='utf-8').read().split('\n'),
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': [
        'scihub = scihub.bin.__init__:main',
    ]},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ]
)