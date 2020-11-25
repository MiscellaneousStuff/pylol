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
from pylol.lib import common
from pylol.lib import portspicker

def to_list(arg):
    return arg if isinstance(arg, list) else [arg]

class Team(enum.IntEnum):
    BLUE = 0
    PURPLE = 1
    NEUTRAL = 2

class Agent(collections.namedtuple("Agent", ["champ", "team"])):
    """Define an Agent. Each agent has a champion and which team it belongs to"""
    def __new__(cls, champion, team):
        return super(Agent, cls).__new__(cls, champion, team)

Dimensions = features.Dimensions
AgentInterfaceFormat = features.AgentInterfaceFormat
parse_agent_interface_format = features.parse_agent_interface_format

class LoLEnv(environment.Base):
    """A League of Legends v4.20 environment.

    The implementation details of the action and observation specs are in
    lib/features.py
    """
    def __init__(self,
                 host=None,
                 map_name=None,
                 players=None,
                 agent_interface_format=None,
                 replay_dir=None,
                 human_observer=False,
                 cooldowns_enabled=False,
                 manacosts_enabled=False,
                 config_path=""):
        """Create a League of Legends v4.20 Env.

        Args:
            map_name: Name of a League of Legends v4.20 map. If non are chosen
                this defaults to `Old Summoners Rift`.
            players: A list of Agent instances that specify who will play.
            replay_dir: Directory for the custom replay file to save to.
        """

        if not host:
            raise ValueError("You must specify a host.")

        if not players:
            raise ValueError("You must specify the list of players.")
            
        for p in players:
            if not isinstance(p, (Agent)):
                raise ValueError(
                    "Expected players to be of type Agent. Got: %s." % p)
        
        if agent_interface_format is None:
            raise ValueError("Please specify agent_interface_format.")
        
        self._agent_interface_format = agent_interface_format

        # num_players = len(players)
        self._num_agents = sum(1 for p in players if isinstance(p, Agent))
        self.players = players

        if not map_name:
            raise ValueError("Missing a map name.")
        
        # Extract directories here
        try:
          with open(config_path) as f:
            game_server_dir, client_dir = f.read().split("\n")
            print("GAMESERVER DIR:", game_server_dir)
            print("CLIENT DIR:", client_dir)
        except:
          raise IOError("Could not open config file: '%s'" % config_path)

        self._map_name = map_name
        self._run_config = run_configs.get(game_server_dir)
        self._game_info = None

        self._launch_game(host=host,
                          human_observer=human_observer,
                          players=players,
                          map_name=map_name,
                          cooldowns_enabled=cooldowns_enabled,
                          manacosts_enabled=manacosts_enabled,
                          game_server_dir=game_server_dir,
                          client_dir=client_dir)

        self._finalize()

    def _finalize(self):
        self._total_steps = 0
        self._episode_steps = 0
        self._episode_count = 0

        self._features = [features.features_from_game_info(
            agent_interface_format=self._agent_interface_format
        )]

        self._last_agent_obs = [None] * self._num_agents
        self._obs = [None] * self._num_agents
        self._agent_obs = [None] * self._num_agents
        self._state = environment.StepType.LAST
        logging.info("Environment is ready.")

    def _launch_game(self, **kwargs):
        """Actually launch the GameServer."""

        # Reserve some ports
        self._ports = portspicker.pick_contiguous_unused_ports(2)
        logging.info("Ports used for GameServer and Redis respectively: %s", self._ports)

        kwargs["host"] = kwargs["host"]
        kwargs["client_port"] = self._ports[0]
        kwargs["redis_port"] = self._ports[1]

        self._lol_procs = [self._run_config.start(**kwargs)]
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
    
    def _step(self):
        return self._observe()

    def step(self, actions):
        """Apply actions, step the world forward, and return observations.

        Args:
            actions: A list of actions meeting the action spec, one per agent, or a
                list per agent. Using a list allows multiple actions per frame, but
                will still check that they're valid, so disabling
                ensure_available actions is encouraged.
        
        Returns:
            A tuple of TimeStep namedtuples, one per agent.
        """

        if self._state == environment.StepType.LAST:
            return self.reset()
        
        """
        actions = [[f.transform_action(o["observation"], a)
                    for a in to_list(acts)]
                   for f, o, acts in zip(self._features, self._obs, actions)]
        """

        new_actions = []
        for o, a in zip(self._obs, actions):
            # print("CURRENT OBS ENV STEP:", o)
            new_actions.append(self._features[0].transform_action(o["observation"], a))

        for c, a in zip(self._controllers, actions):
            c.actions(common.RequestAction(actions=new_actions))

        self._state = environment.StepType.MID
        return self._step()
    
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
        if hasattr(self, "_ports") and self._ports:
            portspicker.return_ports(self._ports)
        self._game_info = None
    
    def _get_observations(self):
        """
        def __observe(c, f):
            obs = c.observe()
            obs = tuple(environment.TimeStep(
                step_type=self._state,
                reward=[0]*self._num_agents,
                discount=1.0,
                observation=obs
            ))
            # obs = CustomObs(obs)
            agent_obs = f.transform_obs(obs)
            return obs, agent_obs

        #print("lol_env.tuple:", __observe(self._controllers, self._features))
        #self._obs, self._agent_obs = __observe(self._controllers[0], self._features)
        res = []
        for c, f in zip(self._controllers, self._features):
            print("c, f:", c, f)
            # res.append(tuple(c, f))
            self._obs, self._agent_obs = __observe(c, f)
        # print("_get_observations.res:", res)
        """

        obs = [self._controllers[0].observe() for _ in self.players]
        #obs = [self._controllers[0].observe()]
        agent_obs = [self._features[0].transform_obs(o) for o in obs]
        
        # Save last observation to calculate rewards
        self._last_agent_obs = self._agent_obs

        # Set new observations
        self._obs, self._agent_obs = obs, agent_obs

    def calc_reward(self, last_obs, obs):
        """Returns the cumulative reward for an observation."""

        reward = 0

        # Winning (+5) Zero-Sum
        winning_weighting = 5.0
        if self._state == environment.StepType.LAST: # Last observation for episode
            if obs["me_unit"].kill_count > obs["enemy_unit"].kill_count:
                winning_reward = winning_weighting
            elif obs["me_unit"].kill_count < last_obs["enemy_unit"].kill_count:
                winning_reward = -winning_weighting
            else:
                winning_reward = 0
            reward += winning_reward
            print("Winning Reward:",
              winning_reward,
              obs["me_unit"].kill_count,
              obs["enemy_unit"].kill_count)

        # Death (-1)
        death_weighting = -1
        if obs["me_unit"].death_count > last_obs["me_unit"].death_count:
            death_reward = death_weighting
        else:
            death_reward = 0
        reward += death_reward
        print("Death Reward:",
              death_reward,
              last_obs["me_unit"].death_count,
              obs["me_unit"].death_count)

        # XP Gained (+0.002) Zero-Sum
        xp_weighting = 0.002
        me_xp_diff = obs["me_unit"].current_xp - last_obs["me_unit"].current_xp
        me_xp_reward = me_xp_diff * xp_weighting
        enemy_xp_diff = obs["enemy_unit"].current_xp - last_obs["enemy_unit"].current_xp
        enemy_xp_reward = -(enemy_xp_diff * xp_weighting)
        xp_reward = me_xp_reward + enemy_xp_reward # Zero-Sum
        reward += xp_reward
        print("XP Reward:", xp_reward)
        
        # Gold Gained (+0.006)
        gold_weighting = 0.006
        gold_diff = obs["me_unit"].current_gold - last_obs["me_unit"].current_gold
        gold_reward = gold_diff * gold_weighting
        reward += gold_reward
        print("Gold Reward:", gold_reward)

        # Health Changed (+2)
        hp_weighting = 2.0
        def hp_change_to_reward(x):
            return (x + 1 - (1 - x)**4) / 2
        cur_hp_diff  = obs["me_unit"].current_hp / obs["me_unit"].max_hp
        last_hp_diff = last_obs["me_unit"].current_hp / last_obs["me_unit"].max_hp
        hp_diff = cur_hp_diff - last_hp_diff
        hp_reward = hp_change_to_reward(hp_diff) * hp_weighting
        reward += hp_reward
        print("HP Reward:", hp_reward, last_obs["me_unit"].current_hp, obs["me_unit"].current_hp)

        # Mana Changed (+0.75)
        mana_weighting = 0.75
        cur_mp_diff  = obs["me_unit"].current_mp / obs["me_unit"].max_mp
        last_mp_diff = last_obs["me_unit"].current_mp / last_obs["me_unit"].max_mp
        mp_diff = cur_mp_diff - last_mp_diff
        mp_reward = mp_diff * mana_weighting
        reward += mp_reward
        print("Mana:", mp_reward, last_obs["me_unit"].current_mp, obs["me_unit"].current_mp)

        # Killed Hero (+1, -0.6)
        kill_weighting = +1
        if obs["me_unit"].kill_count > last_obs["me_unit"].kill_count:
            kill_diff = obs["me_unit"].kill_count - last_obs["me_unit"].kill_count
            kill_reward = kill_diff * kill_weighting
        else:
            kill_reward = 0
        reward += kill_reward
        print("Kill Reward:", kill_reward,
              last_obs["me_unit"].kill_count,
              obs["me_unit"].kill_count)

        # Lane Assignment (-0.15 * seconds out of assigned lane)
        pass
        
        print("Reward:", reward, end = "\n\n")
        return reward

    def _observe(self):
        self._get_observations()
        
        # Automatically make this LAST timestep if someone died as that is end of episode
        # State needs to change before calculating rewards in we start next episode
        if self._controllers[0].someone_died(self._obs[0]["observation"]):
            # print("SOMEONE DIED LOL:", self._state)
            if self._state == environment.StepType.MID:
                self._state = environment.StepType.LAST
            else:
                self._last_agent_obs = [None] * self._num_agents
                self._state = environment.StepType.FIRST

        # Calc reward for current observation(s)
        if self._episode_steps == 0:
            reward = [0] * self._num_agents
        else:
            reward = [self.calc_reward(last, cur) 
                      for last, cur in zip(self._last_agent_obs, self._agent_obs)]
        print("CURRENT REWARD(s):", reward, end = "\n\n\n")

        self._episode_steps += 1
        self._total_steps += 1

        # print("OBS => SOMEONE_DIED:", self._obs)

        # print("lol_env._observe.self._agent_obs :=", self._agent_obs)
        ret_val = tuple(environment.TimeStep(
            step_type=self._state,
            reward=r,
            discount=1,
            observation=o
        ) for r, o in zip(reward, self._agent_obs))

        return ret_val

    def _restart(self):
        # Restart the GameServer controllers
        for c in self._controllers:
            c.restart()

    def reset(self):
        """Starts a new episode."""
        self._episode_steps = 0
        if self._episode_count:
            # No need to restart for the first episode
            self._restart()
        
        self._episode_count += 1

        self._controllers[0].players_reset()

        logging.info("Starting episode %s: on %s" % (self._episode_count, self._map_name))
        self._state = environment.StepType.FIRST

        return self._observe()

    def save_replay(self, replay_dir, prefix=None):
        """Saves a replay to a custom replay file."""
        if prefix is None:
            prefix = self._map_name.replace(" ", "_")
        replay_path = self._run_config.save_replay(
            self._controllers[0].save_replay(), replay_dir, prefix
        )
        logging.info("Wrote replay to: %s", replay_path)
        return replay_path

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
        "CONTENT_PATH": "../../../../Content",
        # "CONTENT_PATH": "/mnt/c/LeagueSandbox/LeagueSandbox-RL-Learning/Content",
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