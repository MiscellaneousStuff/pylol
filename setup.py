# MIT License
# 
# Copyright (c) 2020 MiscellaneousStuff
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module setuptools script."""
from setuptools import setup

description = """PyLoL - League of Legends v4.20 Learning Environment

PyLoL is the Python component of the League of Legends v4.20 Learning Environment
(using a modified version of the LeagueSandbox's GameServer project, not the
original server from Riot). It exposes a custom machine learning API for the
GameServer project as a Python RL Environment. PyLoL provides an interface for RL
agents to interact with the League of Legends v4.20, getting observations and
sending actions.

Read the README at https://github.com/MiscellaneousStuff/pylol for more information.
"""

setup(
    name='pylol-rl',
    version='1.0.0',
    description='PyLoL environment and library for training agents.',
    long_description=description,
    long_description_content_type="text/markdown",
    author='MiscellaneousStuff',
    author_email='raokosan@gmail.com',
    license='MIT License',
    keywords='League of Legends',
    url='https://github.com/MiscellaneousStuff/pylol',
    packages=[
        'pylol',
        'pylol.agents',
        'pylol.bin',
        'pylol.env',
        'pylol.lib',
        'pylol.maps',
        'pylol.run_configs',
        'pylol.tests'
    ],
    install_requires=[
        'absl-py>=0.1.0',
        'numpy>=1.10',
        'six',
        'redis',
        'portpicker'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ]
)