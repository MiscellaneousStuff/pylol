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

import datetime
import os
import uuid

Exists = os.path.exists
IsDirectory = os.path.isdir
ListDir = os.listdir
MakeDirs = os.makedirs
Open = open

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

    def start(self, **kwargs):
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
    
    def abs_replay_path(self, replay_path):
        """Return the absolute path to the replay, outside the sandbox."""
        return os.path.join(self.replay_dir, replay_path)

    def save_replay(self, replay_data, replay_dir, prefix=None):
        """Save a replay to a directory, returning the path to the replay.

        Args:
            replay_data: The result of controller.save_replay(), whch is a serialised
                list of the map, players, multiplier and timestamped actions.
        
        Returns:
            The full path where the replay is saved.
        
        Raises:
            ValueError: If the prefix contains the path separator.
        """

        if not prefix:
            replay_filename = ""
        elif os.path.sep in prefix:
            raise ValueError("Prefix '%s' contains '%s', use replay_dir instead." % (
                prefix, os.path.sep))
        else:
            replay_filename = prefix + "_"
        
        now = datetime.datetime.utcnow().replace(microsecond=0)
        replay_filename += "%s.json" % (now.isoformat("-").replace(":", "-") + "-" + str(uuid.uuid4()))
        replay_dir = self.abs_replay_path(replay_dir)

        if not Exists(replay_dir):
            MakeDirs(replay_dir)
        replay_path = os.path.join(replay_dir, replay_filename)
        with Open(replay_path, "w") as f:
            f.write(replay_data)
        return replay_path