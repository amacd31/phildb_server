import os
from io import open

import versioneer

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

requirements = [
    "phildb",
    "tornado",
    "pandas>=0.17.1",
]

setup(
    name='phildb-server',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='PhilDB timeseries database server',
    long_description=long_description,
    author='Andrew MacDonald',
    author_email='andrew@maccas.net',
    license='BSD',
    url='https://github.com/amacd31/phildb_server',
    install_requires=requirements,
    packages = ['phildb_server'],
    test_suite = 'tests',
    entry_points = {
        'console_scripts': [
            'phildb-server = phildb_server.server:main',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
