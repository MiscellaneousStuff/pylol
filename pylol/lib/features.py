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

        #if not agent_interface_format:
        #    raise ValueError("Please specify agent_interface_format")

        pass
    
    def observation_spec(self):
        """The observation spec for the League of Legends v4.20 environment.
        
        Returns:
            The dict of observation names 
        """

        obs_spec = named_array.NamedDict({
            "game_time": (1,)
        })
        obs_spec["available_actions"] = (0,)

        return obs_spec

    def action_spec(self):
        """The action space pretty complicated and fills the ValidFunctions."""

        act_spec = named_array.NamedDict({
            "empty": (1,)
        })

        return act_spec

    def available_actions(self, obs):
        """Return the list of available action ids."""
        available_actions = set()
        # print("AVAILABLE ACTIONS obs:", obs)
        obs_available_actions = obs["available_actions"]
        print("obs_available_actions:", obs_available_actions)
        if "can_no_op" in obs_available_actions:
            if obs_available_actions["can_no_op"] == True:
                available_actions.add(0)
        """
        print("FUNCTIONS AVAILABLE:", actions.FUNCTIONS_AVAILABLE)
        for i, func in six.iteritems(actions.FUNCTIONS_AVAILABLE):
            if func.avail_fn(obs):
                available_actions.add(i)
        """
        # print("AVAILABLE ACTION IDS:", available_actions)
        return list(available_actions)

    def transform_obs(self, obs):
        """Render some GameServer observations into something an agent can handle."""
        #out = named_array.NamedDict({})

        print("OBS BLUD:", obs["observation"]["game_time"])
        print("AVAILABLE ACTIONS BTW:", self.available_actions(obs["observation"]))

        # Set available actions
        """
        out["available_actions"] = np.array(
          self.available_actions(obs["observation"]), dtype=np.int32)
        """

        obs["available_actions"] = np.array(self.available_actions(obs["observation"]))
        # print("NEW OBS:", obs)
        return obs

    """
    def available_actions(self, obs):
        # Return the list of available action ids. #
        available_actions = set()
        for i, func in six.iteritems(actions.FUNCTIONS_AVAILABLE):
            if func.avail_fn(obs):
                available_actions.add(i)
    """
    
def features_from_game_info():
    """Construct a Features object using data extracted from game info.

    Returns:
        A features object.
    """

    return Features()