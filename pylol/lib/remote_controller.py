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

import sys

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

    def __init__(self, settings, host, port, timeout_seconds, proc=None, kwargs=[]):
        timeout_seconds = timeout_seconds # or FLAGS.lol_timeout
        host = host or "192.168.0.16"
        port = port or 6379
        self.host = host
        self.port = port
        self.pool = redis.ConnectionPool(host=host, port=port, db=0)
        self.r = redis.Redis(connection_pool=self.pool)
        self.timeout = timeout_seconds
        self.settings = settings
        self._last_obs = None
        self._client = None
        self._kwargs = kwargs
        try:
            self._proc = subprocess.Popen(["redis-server", "/mnt/c/Users/win8t/Desktop/AlphaLoL_AI/League of Python/redis.conf"])
        except SubprocessError as e:
            print("Could not open redis. Error message: '%s'" % e)
    
    def close(self):
        """Kill the redis process when the controller is done."""
        self._proc.kill()
        # self._client.kill() doesn't kill the associated league client
    
    def connect(self):
        """Waits until clients can join the GameServer then waits until agents can connect."""

        # Wait until clients can join
        json_txt = self.r.brpop("observation", self.timeout) # Shouldn't be longer than this, will check though
        if json_txt == None:
            print("`clients_join` == NONE")
            raise ConnectionError("Couldn't get `clients_join` message from GameServer")
        else:
            command = json.loads(json_txt[1].decode("utf-8"))
            if command == "clients_join":
                print("`clients_join` == START CLIENT:", command)
                if self._kwargs["human_observer"]:
                    self._client = start_client(host=self.host)
                else:
                    self._client = None
            else:
                print("`clients_join` == WRONG MESSAGE:", command)
                raise ConnectionError("Couldn't get `clients_join` message from GameServer")
        
        # Wait until agents can connect (dependend on how long client takes to load, timing issue...)
        json_txt = self.r.brpop("observation", 60)
        if json_txt == None:
            print("`game_started` == NONE")
            raise ConnectionError("Couldn't get `game_started` message from GameServer")
        else:
            command = json.loads(json_txt[1].decode("utf-8"))
            if command == "game_started":
                print("`game_started` == START CLIENT:", command)
                print("Running AI agents")
            else:
                print("`game_started` == WRONG MESSAGE:", command)
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

        # Start observing if we haven't already.
        if self._last_obs == None:
            self.r.delete("action") # Reset action pipe
            self.r.delete("observation") # Reset observation pipe
            self.r.lpush("command", "start_observing") # Start observing

            self.players_reset()

        # Get the observation
        json_txt = self.r.brpop("observation", self.timeout)
        if json_txt == None:
            print("Error: Observation timed out")
            return None
        else:
            obs = json.loads(json_txt[1].decode("utf-8"))
            
            # Print first observation for testing...
            # if self._last_obs == None: print("FIRST OBSERVATION:", obs)
            
            self._last_obs = obs
            return obs
    
    def actions(self, req_action):
        """Send an action request, which may include multiple actions."""
        if FLAGS.lol_log_actions and req_action.actions:
            sys.stderr.write(" Sending actions ".center(60, ">") + "\n")
            for action in req_action.actions:
                sys.stderr.write(str(action))
        
        """Actually perform the actions here."""
        for action in req_action.actions:
            action = action.props
            if action["type"] == "no_op":
                pass
            elif action["type"] == "move":
                playerId = action["user_id"]
                x = action["move_range"].x - 4
                y = action["move_range"].y - 4
                self.player_move(playerId, x, y)
            elif action["type"] == "spell":
                playerId = action["user_id"]
                spell_slot = action["spell"]
                x = action["position"].x
                y = action["position"].y
                self.player_spell(playerId, 2, spell_slot, x, y)

    def act(self, action):
        """Send a single action. This is a shortcut for `actions`."""
        if action:
            return self.actions(action)
        
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
        #print("player_move: ", id, x, y, self.r)
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

    def restart(self):
        # No support for outright restarting the game within the GameServer at the moment
        pass

    def save_replay(self):
        """Save a replay, returning the data."""
        command = {
            "map": str("map"),
            "players": str("players"),
            "multiplier": float(7.5)
        }
        self.r.lpush("command", "save_replay")
        self.r.lpush("command", json.dumps(command))

        replay_json = self.r.brpop("command_data", self.timeout)
        print("REPLAY JSON", replay_json)
        if replay_json == None:
            raise ConnectionError("GameServer couldn't provide replay json data")
        
        replay_json = replay_json[1].decode("utf-8")
        return replay_json

def start_client(host="localhost", port="5119", playerId="1"):
    LeagueOfLegendsClient = None
    LeagueOfLegendsClientArgs = [
        "./League of Legends.exe",
        "8394",
        "",
        "",
        "{0} {1} 17BLOhi6KZsTtldTsizvHg== {2}".format(host, port, playerId)
    ]
    LeagueOfLegendsClient = subprocess.Popen(LeagueOfLegendsClientArgs, cwd="/mnt/c/LeagueSandbox/League_Sandbox_Client/RADS/solutions/lol_game_client_sln/releases/0.0.1.68/deploy/")
    return LeagueOfLegendsClient