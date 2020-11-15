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
"""Protocol library to make communication easy."""

from absl import flags

import redis
import json

import sys

flags.DEFINE_integer("lol_verbose_protocol", 0,
                     ("Print the communication packets with LoL. 0 disables. "
                      "-1 means all. >0 will print that many lines per"
                      "packet."))
FLAGS = flags.FLAGS

class ConnectionError(Exception):
    """Failed to connect to the redis server."""
    pass

class LoLProtocol(object):
    """Defines the protocol for chatting with the redis server that communicates with starcraft."""

    def __init__(self, host="localhost", port=6379, timeout=1):
        self.pool = redis.ConnectionPool(host=host, port=port, db=0)
        self.r = redis.Redis(connection_pool=self.pool)
        self.timeout = timeout
    
    def log(self, s, *args):
        """Log a string"""
        sys.stderr.write((s + "\n") % args)
        sys.stderr.flush()
    
    def read(self):
        """  """
        pass