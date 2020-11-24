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
"""Hardcoded scripted agent."""

import numpy

from pylol.agents import base_agent
from pylol.lib import actions
from pylol.lib import features
from pylol.lib import point

FUNCTIONS = actions.FUNCTIONS

class ScriptedAgent(base_agent.BaseAgent):
    """Throws Q's at the other player at the moment."""

    def step(self, obs):
        super(ScriptedAgent, self).step(obs)
        
        me_position = point.Point(obs.observation["me_unit"].position_x,
                       obs.observation["me_unit"].position_y)

        enemy_position = point.Point(obs.observation["enemy_unit"].position_x,
                          obs.observation["enemy_unit"].position_y)

        return actions.FunctionCall(2, [[0], enemy_position])