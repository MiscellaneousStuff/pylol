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
"""A base env wrapper so we don't need to override everything every time."""

from pylol.env import environment

class BaseEnvWrapper(environment.Base):
    """A base env wrapper so we don't need to override everything every time."""

    def __init__(self, env):
        self.env = env
    
    def close(self, *args, **kwargs):
        return self.env.close(*args, **kwargs)
    
    def action_spec(self, *args, **kwargs):
        return self.env.action_spec(*args, **kwargs)

    def observation_spec(self, *args, **kwargs):
        return self.env.observation_spec(*args, **kwargs)
    
    def reset(self, *args, **kwargs):
        return self.env.reset(*args, **kwargs)
    
    def step(self, *args, **kwargs):
        return self.env.step(*args, **kwargs)
    
    def save_replay(self, *args, **kwargs):
        return self.env.save_replay(*args, **kwargs)
    
    @property
    def state(self):
        return self.env.state