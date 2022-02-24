#!/usr/bin/env python
# coding=utf-8

import glob
import os
from setuptools import setup


PLUGIN_DIR = "OMEXP_plugins"


def find_files(directory):
    """Find all files in a directory

    Similar to glob.glob(f"{directory}/**", recursive=True)) when available
    """
    for root, dirs, files in os.walk(directory):
        for basename in files:
            yield os.path.join(root, basename)


# Define which files to copy to the opensesame_plugins directory.
# This is a list of tuples where each tuple looks like this:
# First the target folder.
# Then a list of files that are copied into the target folder. Make sure
# that these files are also included by MANIFEST.in!
# Example entry:
#     ("share/opensesame_plugins/calibration", [
#         "OMEXP_plugins/calibration/info.yaml",
#         "OMEXP_plugins/calibration/calibration_large.png",
#         ...
#     ])
data_files = [(
        os.path.join("share/opensesame_plugins", plugin),
        list(find_files(os.path.join(PLUGIN_DIR, plugin)))
    ) for plugin in os.listdir(PLUGIN_DIR)
]

setup(
    name='opensesame-plugin-omexp',
    version='0.1.0',
    description='BRM_OMEXP plugins for OpenSesame',
    author='Eleonora Sulas',
    author_email='elus@oticonmedical.com',
    url='https://github.com/elus-om/BRM_OMEXP',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    data_files=data_files
)
