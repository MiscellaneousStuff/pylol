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
"""Features used for ML"""

import collections
from absl import logging
import random
import six

import enum
import numpy as np
from pylol.lib import actions
from pylol.lib import named_array
from pylol.lib import point

class Features(object):
    """Render feature layers from GameServer observation into numpy arrays."""

    def __init__(self):
        """Initialize a Features instance matching the specified interface format.

        Args:
            agent_interface_format: See the documentation for `AgentInterfaceFormat`.

        Raises:
            ValueError: if agent_interface_format isn't specified.
        """

        if not agent_interface_format:
            raise ValueError("Please specify agent_interface_format")
    
    def observation_spec(self):
        """The observation spec for the League of Legends v4.20 environment.
        
        Returns:
            The dict of observation names 
        """

        obs_spec = named_array.NamedDict({
            "game_time": (0,),
            "me": (0,),
            "enemy": (0,)
        })
    def action_spec(self):
        """The action space pretty complicated and fills the ValidFunctions."""
        return self.valid_functions
    
    def available_actions(self, obs):
        """Return the list of available action ids."""
        available_actions = set()
        for i, func in six.iteritems(actions.FUNCTIONS_AVAILABLE):
            if func.avail_fn(obs):
                available_actions.add(i)