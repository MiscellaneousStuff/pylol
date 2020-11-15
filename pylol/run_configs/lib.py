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
"""Configs for various ways to run League of Legends v4.20."""

class RunConfig(object):
    """Base class for different run configs."""

    def __init__(self, replay_dir, cwd=None, env=None):
        """Initialize the runconfig with the various directories needed.
        
        Args: Where to find the custom replays for the pylol project, not the
        same as actual Legends of Legends v4.20 replays.
        """
        self.replay_dir = replay_dir
        self.cwd = cwd
        self.env = env

    def start(self):
        raise NotImplementedError()
    
    @classmethod
    def priority(cls):
        """None means this isn't valid. Run the one with the max priority."""
        return None
        
    @classmethod
    def all_subclasses(cls):
        """An iterator over all subclasses of `cls`."""
        for s in cls.__subclasses__():
            yield s
            for c in s.all_subclasses():
                yield c
    
    @classmethod
    def name(cls):
        return cls.__name__