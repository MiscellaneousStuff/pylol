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
"""Configs for how to run League of Legends v4.20 from a custom directory on
various platforms"""

import os

from pylol.lib import lol_process
from pylol.run_configs import lib

class LocalBase():
    """Base run config for installs."""

    def __init__(self, exec_dir, exec_name):
        exec_dir = os.path.expanduser(exec_dir)
        self.exec_dir = exec_dir
        self.exec_name = exec_name
        
    def start(self):
        """Launch the game."""
        if not os.path.isdir(self.exec_dir):
            raise lol_process.LoLLaunchError(
                "Failed to run League of Legends at '%s" % self.exec_dir)
        
        if not os.path.exists(self.exec_dir):
            raise lol_process.LoLLaunchError("No LoL binary found at: %s" % self.exec_path)
        
        exec_path = self.exec_dir + self.exec_name

        return lol_process.LoLProcess(self, exec_path=exec_path)

class Windows(LocalBase):
    """Run on windows."""

    def __init__(self, exec_path):
        super(Windows, self).__init__(exec_path, "League of Legends.exe")

class Linux(LocalBase):
    """Config to run on Linux."""
    
    def __init__(self, exec_path):
        super(Linux, self).__init__(exec_path, "./League of Legends.exe")