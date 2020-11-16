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
"""Controllers take actions and generates observations."""

from absl import logging

from absl import flags
# from pylol.lib import protocol

import redis
import json
import subprocess
from subprocess import SubprocessError

flags.DEFINE_bool("lol_log_actions", False, "Print all actinos sent to GameServer.")
flags.DEFINE_integer("lol_timeout", 60, "Timeout to connect and wait for RPC responses.")
FLAGS = flags.FLAGS

class ConnectError(Exception):
    pass

class RequestError(Exception):
    def __init__(self, desc, res):
        super(RequestError, self).__init__(desc)
        self.res = res

class RemoteController(object):
    """Implements a python interface to interact with the GameServer binary.

    Currently uses Redis to manage this.

    All of these are implemented as blocking calls, so wait for the response
    before returning.
    """

    def __init__(self, settings, host, port, proc=None, timeout_seconds=1):
        timeout_seconds = timeout_seconds # or FLAGS.lol_timeout
        host = host or "localhost"
        port = port or 6379
        self.host = host
        self.port = port
        self.pool = redis.ConnectionPool(host=host, port=port, db=0)
        self.r = redis.Redis(connection_pool=self.pool)
        self.timeout = timeout_seconds
        self.running = True
        self.settings = settings
        self.last_obs = None
        try:
            self._proc = subprocess.Popen(["redis-server", "/mnt/c/Users/win8t/Desktop/AlphaLoL_AI/League of Python/redis.conf"])
        except SubprocessError as e:
            print("Could not open redis. Error message: '%s'" % e)
    
    def close(self):
        """Kill the redis process when the controller is done."""
        self._proc.kill()
    
    def connect(self):
        """Waits until clients can join the GameServer then waits until agents can connect."""

        # Wait until clients can join
        json_txt = self.r.brpop("observation", 20) # Shouldn't be longer than this, will check though
        if json_txt == None:
            raise ConnectionError("Couldn't get `clients_join` message from GameServer")
        else:
            command = json.loads(json_txt[1].decode("utf-8"))
            if command == "clients_join":
                print("Start client and join game")
            else:
                raise ConnectionError("Couldn't get `clients_join` message from GameServer")
        
        # Wait until agents can connect (dependend on how long client takes to load, timing issue...)
        json_txt = self.r.brpop("observation", 20)
        if json_txt == None:
            raise ConnectionError("Couldn't get `game_started` message from GameServer")
        else:
            command = json.loads(json_txt[1].decode("utf-8"))
            if command == "game_started":
                print("Running AI agents")
            else:
                raise ConnectionError("Couldn't get `game_started` message from GameServer")

    # Check if someone died for this observation
    def someone_died(self, observation):
        champ_units = observation["champ_units"]
        for champ_unit in champ_units:
            if champ_unit["alive"] == 0.0:
                return True
        return False

    def observe(self):
        """Get a current observation."""
        # obs = Get Observation
        # self.last_obs = obs

        # Start observing if we haven't already.
        if self.last_obs == None:
            self.r.delete("action") # Reset action pipe
            self.r.delete("observation") # Reset observation pipe
            self.r.lpush("command", "start_observing") # Tell the server to start
                                                    # ... accepting actions and observations

        # Get the observation
        json_txt = self.r.brpop("observation", self.timeout)
        if json_txt == None:
            self.running = False
            print("Error: Observation timed out")
            return None
        else:
            last_obs = json.loads(json_txt[1].decode("utf-8"))
            self.last_obs = last_obs
            return last_obs
    
    def quit(self):
        """Shut down the redis process."""
        self.r = None
        self._proc.kill()
    
    def player_attack(self, player_id, target_player_id):
        action = {
            "player_id": str(player_id),
            "target_player_id": str(target_player_id)
        }
        self.r.lpush("action", "attack")
        self.r.lpush("action", json.dumps(action))
        return {"type": "attack", "data": action}

    def player_spell(self, player_id, target_player_id, spell_slot, x, y):
        action = {
            "player_id": str(player_id),
            "target_player_id": str(target_player_id),
            "spell_slot": int(spell_slot),
            "x": float(x * 1.0),
            "y": float(y * 1.0)
        }
        self.r.lpush("action", "spell")
        self.r.lpush("action", json.dumps(action))
        return {"type": "spell", "data": action}

    def players_reset(self):
        self.r.lpush("action", "reset")
        self.r.lpush("action", "")

    def player_move(self, player_id, x, y):
        action = {
            "player_id": str(player_id),
            "x": float(x * 100.0),
            "y": float(y * 100.0)
        }
        self.r.lpush("action", "move")
        self.r.lpush("action", json.dumps(action))
        return {"type": "move", "data": action}

    def player_move_to(self, player_id, x, y):
        action = {
            "player_id": str(player_id),
            "x": float(x),
            "y": float(y)
        }
        self.r.lpush("action", "move_to")
        self.r.lpush("action", json.dumps(action))

    def player_teleport(self, player_id, x, y):
        action = {
            "player_id": str(player_id),
            "x": float(x),
            "y": float(y)
        }
        self.r.lpush("action", "teleport")
        self.r.lpush("action", json.dumps(action))

    def player_noop(self, n=1):
        for i in range(n):
            self.r.lpush("action", "noop")
            self.r.lpush("action", "")
        return {"type": "noop", "data": ""}

    def player_change(self, player_id, champion_name):
        command = {
            "player_id": player_id,
            "champion_name": champion_name
        }
        self.r.lpush("command", "change_champion")
        self.r.lpush("command", json.dumps(command))