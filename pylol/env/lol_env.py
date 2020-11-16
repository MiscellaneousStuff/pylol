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
"""A League of Legends v4.20 environment."""

import collections
from absl import logging
import random
import time

import enum

from pylol import maps
from pylol import run_configs
from pylol.env import environment
from pylol.lib import features

class Team(enum.IntEnum):
    BLUE = 0
    PURPLE = 1
    NEUTRAL = 2

class Agent(collections.namedtuple("Agent", ["champion", "team"])):
    """Define an Agent. Each agent has a champion and which team it belongs to"""
    def __new__(cls, champion, team):
        return super(Agent, cls).__new__(cls, champion, team)

class LoLEnv(environment.Base):
    """A League of Legends v4.20 environment.

    The implementation details of the action and observation specs are in
    lib/features.py
    """
    def __init__(self,
                 map_name=None,
                 players=None,
                 replay_dir=None):
        """Create a League of Legends v4.20 Env.

        Args:
            map_name: Name of a League of Legends v4.20 map. If non are chosen
                this defaults to `Old Summoners Rift`.
            players: A list of Agent instances that specify who will play.
            replay_dir: Directory for the custom replay file to save to.
        """

        if not players:
            raise ValueError("You must specify the list of players.")
            
        for p in players:
            if not isinstance(p, (Agent)):
                raise ValueError(
                    "Expected players to be of type Agent. Got: %s." % p)
        
        num_players = len(players)
        self.num_agents = sum(1 for p in players if isinstance(p, Agent))
        self.players = players

        if not map_name:
            raise ValueError("Missing a map name.")
        
        self._map_name = map_name
        self._run_config = run_configs.get()
        self._game_info = None
        
        self._launch_game()

        self._finalize()

    def _finalize(self):
        self.total_steps = 0
        self.episode_steps = 0
        self.episode_count = 0
        self._features = [features.features_from_game_info()]
        self.obs = [None] * self.num_agents
        self.state = environment.StepType.LAST
        logging.info("Environment is ready.")

    def _launch_game(self):
        """Actually launch the GameServer."""
        self._lol_procs = [self._run_config.start()]
        self._controllers = [p.controller for p in self._lol_procs]
    
    @property
    def map_name(self):
        """Get the current map name."""
        return self._map_name
    
    @property
    def game_info(self):
        return self._game_info
    
    def observation_spec(self):
        """Look at Features for full spec."""
        return tuple(f.observation_spec() for f in self._features)
    
    def action_spec(self):
        """Look at Features for full spec."""
        return tuple(f.action_spec() for f in self._features)
    
    def step(self):
        """Apply actions, step the world forward, and return observations.

        Args:
            actions: A list of actions meeting the action spec, one per agent, or a
                list per agent. Using a list allows multiple actions per frame, but
                will still check that they're valid, so disabling
                ensure_available actions is encouraged.
        
        Returns:
            A tuple of TimeStep namedtuples, one per agent.
        """

        if self.state == environment.StepType.LAST:
            return self.reset()
    
    def close(self):
        logging.info("Environment Close")
        if hasattr(self, "_controllers") and self._controllers:
            for c in self._controllers:
                c.quit()
            self._controllers = None
        if hasattr(self, "_lol_procs") and self._lol_procs:
            for p in self._lol_procs:
                p.close()
            self.lol_procs = None
        self._game_info = None
    
    def observe(self):
        self.episode_steps += 1
        self.total_steps += 1

    def reset(self):
        """Starts a new episode."""
        self.episode_steps = 0
        if self.episode_count:
            pass # self.restart() # "To support fast restart of mini-games"
        
        self.episode_count += 1
        self.state = environment.StepType.FIRST
        return self.observe()


MAP = {
    "Old Summoners Rift": 1,
    "New Summoners Rift": 11,
    "Howling Abyss": 12
}

TEAM = {
    "BLUE": "BLUE",
    "PURPLE": "PURPLE"
}

SUMMONER_SPELL = {
    "FLASH": "SummonerFlash",
    "HEAL": "SummonerHeal",
    "IGNITE": "SummonerDot"
}

def LoLEnvSettingsPlayer(
    playerId,
    name,
    champion,
    team,
    rank="DIAMOND",
    skin=0,
    summoner1=SUMMONER_SPELL["FLASH"],
    summoner2=SUMMONER_SPELL["HEAL"],
    ribbon=2,
    icon=0
):
    return {
        "playerId": playerId,
        "blowfishKey": "17BLOhi6KZsTtldTsizvHg==",
        "rank": rank,
        "name": name,
        "champion": champion,
        "team": team,
        "skin": skin,
        "summoner1": summoner1,
        "summoner2": summoner2,
        "ribbon": ribbon,
        "icon": icon,
        "runes": {
            "1": 5245,
            "2": 5245,
            "3": 5245,
            "4": 5245,
            "5": 5245,
            "6": 5245,
            "7": 5245,
            "8": 5245,
            "9": 5245,
            "10": 5317,
            "11": 5317,
            "12": 5317,
            "13": 5317,
            "14": 5317,
            "15": 5317,
            "16": 5317,
            "17": 5317,
            "18": 5317,
            "19": 5289,
            "20": 5289,
            "21": 5289,
            "22": 5289,
            "23": 5289,
            "24": 5289,
            "25": 5289,
            "26": 5289,
            "27": 5289,
            "28": 5335,
            "29": 5335,
            "30": 5335
        }
    }

def LoLEnvSettingsGameInfo(
    manacosts_enabled=False,
    cooldowns_enabled=False,
    minion_spawns_enabled=False,
    cheats_enabled=True,
    is_damage_text_global=True
):
    return {
        "MANACOSTS_ENABLED":        manacosts_enabled,
        "CHEATS_ENABLED":           cheats_enabled,
        "COOLDOWNS_ENABLED":        cooldowns_enabled,
        "MINION_SPAWNS_ENABLED":    minion_spawns_enabled,
        # "CONTENT_PATH": "../../../../Content",
        "CONTENT_PATH": "/mnt/c/LeagueSandbox/LeagueSandbox-RL-Learning/Content",
        "IS_DAMAGE_TEXT_GLOBAL":    is_damage_text_global
    }

def LoLEnvSettingsGame(
    map=MAP["Old Summoners Rift"]
):
    return {
        "map": map,
        "dataPackage": "LeagueSandbox-Scripts"
    }

def LoLEnvSettings(players, game, gameInfo):
    return {
        "players": players,
        "game": game,
        "gameInfo": gameInfo
    }