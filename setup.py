import os
from io import open

import versioneer

from setuptools import setup

requirements = [
    "phildb",
    "tornado",
    "pandas>=0.17.1",
]

setup(
    name='phildb_server',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='PhilDB timeseries database server',
    author='Andrew MacDonald',
    author_email='andrew@maccas.net',
    license='BSD',
    url='https://github.com/amacd31/phildb_server',
    install_requires=requirements,
    packages = ['phildb_server'],
    test_suite = 'tests',
    scripts=[
        'bin/phildb-server',
    ],
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
