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
from pylol.lib import common

class Features(object):
    """Render feature layers from GameServer observation into numpy arrays."""

    def __init__(self):
        self._valid_functions = _init_valid_functions()
    
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
        return self._valid_functions

    def available_actions(self, obs):
        """Return the list of available action ids."""
        available_actions = set()
        obs_available_actions = obs["available_actions"]
        if obs_available_actions["can_no_op"]: available_actions.add(0)
        # if obs_available_actions["can_move"]: available_actions.add(1)
        """
        print("FUNCTIONS AVAILABLE:", actions.FUNCTIONS_AVAILABLE)
        for i, func in six.iteritems(actions.FUNCTIONS_AVAILABLE):
            if func.avail_fn(obs):
                available_actions.add(i)
        """
        
        return list(available_actions)

    def transform_action(self, obs, func_call):
        """Transform an agent-style action to one that GameServer can consume.

        Args:
            obs: an observation extracted from redis from the previous step.
            func_call: a `FunctionCall` to be turned into a a redis action.
        
        Returns:
            a corresponding `common.Action`.
        
        Raises:
            ValueError: if the action doesn't pass validation.
        """

        # Valid id?
        func_id = func_call.function
        try:
            func = actions.FUNCTIONS[func_id]
        except KeyError:
            raise ValueError("Invalid function: %s." % func_id)
            
        # Correct number of args?
        if len(func_call.arguments) != len(func.args):
            raise ValueError(
                "Wrong number of arguments for function: %s, got: %s" % (
                    func, func_call.arguments))
        
        # Args are valid?
        for t, arg in zip(func.args, func_call.arguments):
            if t.count:
                if 1 <= len(arg) <= t.count:
                    continue
            else:
                raise ValueError(
                    "Wrong number of values for argument of %s, got: %s" % (
                        func, func_call.arguments))
            sizes = t.sizes
            if len(sizes) != len(arg):
                raise ValueError(
                    "Wrong number of values for argument of %s, got: %s" % (
                        func, func_call.arguments))
            for s, a in zip(sizes, arg):
                if not np.all(0 <= a) and np.all(a < s):
                    raise ValueError("Argument is out of range for %s, got: %s" % (
                        func, func_call.arguments))

        # Convert them to python types
        kwargs = {type_.name: type_.fn(a)
              for type_, a in zip(func.args, func_call.arguments)}
        
        # redis magic...
        lol_action = common.Action()

        kwargs["action"] = lol_action

        actions.FUNCTIONS[func_id].function_type(**kwargs)

        return lol_action

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

def _init_valid_functions():
    """Initialize ValidFunctions and set up the callbacks."""
    sizes = {
        "position": tuple([0, 0])
    }

    types = actions.Arguments(*[
        actions.ArgumentType.spec(t.id, t.name, sizes.get(t.name, t.sizes))
        for t in actions.TYPES])
    
    print("TYPES:", types)
    print("actions.Functions:", actions.Functions)
    print("actions.FUNCTIONS:", list(actions.FUNCTIONS))

    items = [
        actions.Function.spec(f.id, f.name, tuple(types[t.id] for t in f.args))
        for f in actions.FUNCTIONS]

    print("items:", items)

    functions = actions.Functions(items)
    
    return actions.ValidActions(types, functions)
    
def features_from_game_info():
    """Construct a Features object using data extracted from game info.

    Returns:
        A features object.
    """

    return Features()