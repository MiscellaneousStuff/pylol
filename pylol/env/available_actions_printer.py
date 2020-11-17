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
"""An env wrapper to print the available actions."""

from pylol.env import base_env_wrapper

class AvailableActionsPrinter(base_env_wrapper.BaseEnvWrapper):
    """An env wrapper to print the available actions."""

    def __init__(self, env):
        super(AvailableActionsPrinter, self).__init__(env)
        self.seen = set()
        self.action_spec = self.action_spec()[0]
    
    def step(self, *args, **kwargs):
        all_obs = super(AvailableActionsPrinter, self).step(*args, **kwargs)
        for obs in all_obs:
            for avail in obs["available_actions"]:
                if avail not in self.seen:
                    self.seen.add(avail)
                    self.print(self.action_spec.functions[avail].str(True))
        return all_obs
    
    def print(self, s):
        print(s)