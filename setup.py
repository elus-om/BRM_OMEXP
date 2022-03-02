#!/usr/bin/env python
# coding=utf-8

import glob
import os
from setuptools import setup


PLUGIN_DIR = "OMEXP_plugins"

with open("READMEpypi.md") as f:
    LONG_DESCRIPTION = f.read()

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
    version='0.1.4post1',
    description='BRM_OMEXP plugins for OpenSesame',
    long_description_content_type = 'text/markdown',
    long_description=LONG_DESCRIPTION,
    author='Eleonora Sulas & Pierre-Yves Hasan',
    author_email='elus@oticonmedical.com',
    url='https://github.com/elus-om/BRM_OMEXP',
    install_requires=[
          'numba>=0.51.2',
          'liesl>=0.3.4.6',
          'rtmixer>=0.1.2',
          'resampy>=0.2.2',
          'soundfile>=0.10.3.post1',
          'sounddevice>=0.4.1',
          'scipy==1.1.0',
          'numpy==1.18.1',
      ],
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
    ],
    data_files=data_files
)
