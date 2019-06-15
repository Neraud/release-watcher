import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'),
                      fd.read())


setup(
    name="release_watcher",
    version="0.1.0",
    url="https://github.com/Neraud/release-watcher",
    license='MIT',
    author="Neraud",
    description="An application to watch for releases",
    long_description=read("README.md"),
    packages=find_packages(exclude=('tests', )),
    install_requires=[
        'requests==2.22.0',
        'pyyaml==5.1.1',
        'Click==7.0',
        'www-authenticate==0.9.2',
        'python-dateutil==2.6.0',
        'prometheus_client==0.7.0',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points='''
        [console_scripts]
        release_watcher = release_watcher.release_watcher:main
    ''',
)
