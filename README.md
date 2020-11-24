# PyLoL - League of Legends v4.20 Learning Environment
PyLoL is the Python component of the League of Legends v4.20 Learning Environment (using a modified version of the LeagueSandbox's GameServer project, not the original server from Riot). It exposes a custom machine learning API for the GameServer project as a Python RL Environment. PyLoL provides an interface for RL agents to interact with the League of Legends v4.20, getting observations and sending actions.

## About

Disclaimer: This project is not affiliated with Riot Games in any way.

If you are interested in using this project or are just curious,
send an email to [raokosan@gmail.com](mailto:raokosan@gmail.com).

# Quick Start Guide

## Google Colab

The easiest way to try pylol at the moment is to visit this Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MiscellaneousStuff/pylol/blob/main/demonstration.ipynb)

Within the demonstration, you can try different agents by changing the "--agent"
parameter to either random, base or scripted. Random will choose random actions
from the action space uniformly, base will just issue no-ops (i.e. no operation,
it will do nothing) and scripted will have the agents just attack each other.

## Get PyLoL

### From Source

You can install PyLoL from a local clone of the git repo:

```shell
git clone https://github.com/MiscellaneousStuff/pylol.git
pip3 install --upgrade pylol/
```