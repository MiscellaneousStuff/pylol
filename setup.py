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
    name='PyLoL',
    version='1.0.0',
    description='PyLoL environment and library for training agents.',
    long_description=description,
    author='MiscellaneousStuff',
    author_email='raokosan@gmail.com',
    license='MIT License',
    keywords='League of Legends',
    url='https://github.com/MiscellaneousStuff/pylol',
    packages=[
        'pylol',
    ]
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ]
)
