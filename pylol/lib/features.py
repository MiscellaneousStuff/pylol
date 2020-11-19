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

class AgentInterfaceFormat(object):
    """Observation and action interface format specific to a particular agent."""
    
    def __init__(self, feature_dimensions=None):
        """Initializer.

        Args:
            feature_dimensions: Feature layer `Dimension`.
        """
        if not feature_dimensions:
            raise ValueError("Must set feature dimensions")
            
        self._feature_dimensions = feature_dimensions
        self._action_dimensions = feature_dimensions

    @property
    def feature_dimensions(self):
        return self._feature_dimensions
    
    @property
    def action_dimensions(self):
        return self._action_dimensions

def parse_agent_interface_format(feature_map=None):
    """Creates an AgentInterfaceFormat object from keyword args.

    Convenient when using dictionaries or command-line arguments for config.

    Note that the feature_* and rgb_* properties define the respective spatial
    observation dimensions and accept:
        * None or 0 to disable that spatial observation.
        * A single int for a square observation with that side length.
        * A (int, int) tuple for a rectangular (width, height) observation.

    Args:
        feature_map: Map dimensions.
    
    Returns:
        An `AgentInterfaceFormat` object.
    
    Raises:
    ValueError: If an invalid parameter is specified.
    """
    if feature_map:
        feature_dimensions = Dimensions(feature_map)
    else:
        feature_dimensions = None
    
    return AgentInterfaceFormat(feature_dimensions=feature_dimensions)

def _to_point(dims):
  """Convert (width, height) or size -> point.Point."""
  assert dims

  if isinstance(dims, (tuple, list)):
    if len(dims) != 2:
      raise ValueError(
          "A two element tuple or list is expected here, got {}.".format(dims))
    else:
      width = int(dims[0])
      height = int(dims[1])
      if width <= 0 or height <= 0:
        raise ValueError("Must specify +ve dims, got {}.".format(dims))
      else:
        return point.Point(width, height)
  else:
    size = int(dims)
    if size <= 0:
      raise ValueError(
          "Must specify a +ve value for size, got {}.".format(dims))
    else:
      return point.Point(size, size)

class Dimensions(object):
    """Map dimensions configuration.

    Map dimensions must be specified. Sizes must be positive.

    Attributes:
        map: A (width, height) int tuple or a single int to be used.
    """

    def __init__(self, map=None):
        if not map:
            raise ValueError("map must be set, map={}".format(map))
    
        self._map = _to_point(map)

    @property
    def map(self):
        return self._map
    
    def __repr__(self):
        return "Dimensions(map={})".format(self.map)

    def __eq__(self, other):
        return (isinstance(other, Dimensions) and self.screen == other.screen)

    def __ne__(self, other):
        return not self == other

class Features(object):
    """Render feature layers from GameServer observation into numpy arrays."""

    def __init__(self, agent_interface_format=None):
        """Initialize a Features instance matching the specified interface format.

        Args:
            agent_interface_format: See the documentation for `AgentInterfaceFormat`.
        """
        if not agent_interface_format:
            raise ValueError("Please specify agent_interface_format")
        
        self._agent_interface_format = agent_interface_format
        aif = self._agent_interface_format

        print("AIF:", aif)
        self._valid_functions = _init_valid_functions(aif.action_dimensions)
    
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
        if obs_available_actions["can_move"]: available_actions.add(1)
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
        aif = self._agent_interface_format
        print("FUNC:", func.args, func_call.arguments)
        for t, arg in zip(func.args, func_call.arguments):
            if t.name in ("position"):
                sizes = aif.action_dimensions.map
            else:
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

        print("kwargs:", kwargs)
        a = actions.FUNCTIONS[func_id].function_type(**kwargs)
        print("kwargs a:", a)

        return lol_action

    def transform_obs(self, obs):
        """Render some GameServer observations into something an agent can handle."""
        #out = named_array.NamedDict({})

        # print("OBS BLUD:", obs["observation"]["game_time"])
        print("AVAILABLE ACTIONS BTW:", self.available_actions(obs["observation"]))

        # Set available actions
        """
        out["available_actions"] = np.array(
          self.available_actions(obs["observation"]), dtype=np.int32)
        """

        obs["available_actions"] = np.array(self.available_actions(obs["observation"]))
        # print("NEW OBS:", obs)
        return obs

def _init_valid_functions(action_dimensions):
    """Initialize ValidFunctions and set up the callbacks."""
    sizes = {
        "position": tuple(int(i) for i in action_dimensions.map)
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
    
def features_from_game_info(agent_interface_format=None):
    """Construct a Features object using data extracted from game info.

    Returns:
        A features object.
    """

    return Features(agent_interface_format=agent_interface_format)