#! /usr/bin/python

from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='UTBMStudentsControlConsole',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="1.0",
    description="A Raspberry Pi-powered console to control students attendance",
    long_description="This project consists in designing, building and programming a full portable console allowing the University of Technology of Belfort-Montbeliard (France) staff to control students attendance at some mandatory events.  \
    This project involves Raspberry Pi programming through Python, 3D printing, and electronics.",

    # The project's main homepage.
    url="https://github.com/totordudu/UTBM_TZ20",

    # Author details
    author='T.D-V.M',
    author_email='valentin.mercy at utbm.fr',

    # Choose your license
    license='GNU GPL v3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Teachers',
        'Topic :: attendance control',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7'
    ],

    # What does your project relate to?
    keywords='attendance control university',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages('.', exclude=['contrib', 'docs', 'tests*']),
    packages=find_packages() ,

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['configparser','treelib', 'spidev', 'psutil','pyudev','requests','shutils'],

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require = {
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #  package_data={
    #      'refnumtool':['data/doc/html/*.html',
    #                    'data/doc/html/*.js',
    #                    'data/doc/html/_images/*',
    #                    'data/doc/html/_modules/*.html',
    #                    'data/doc/html/_sources/*','data/doc/html/_static/*',
    #                    'data/doc/html/_modules/refnumtool/*']
    #  },
    #  scripts = ['scripts/run_refnumtool.sh','scripts/run_refnumtool.bat'],
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('doc', ['LICENSE.txt'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)