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
"""Test run the client."""

import os

from absl import flags
from absl import app

from pylol.agents import base_agent, random_agent, scripted_agent
from pylol.env import lol_env
from pylol.env import run_loop
from pylol.lib import point_flag

FLAGS = flags.FLAGS
point_flag.DEFINE_point("feature_map_size", "16000",
                        "Resolution for screen feature layers.")
point_flag.DEFINE_point("feature_move_range", "8",
                        "Resolution for screen feature layers.")
flags.DEFINE_string("players", "Ezreal.BLUE,Ezreal.PURPLE", "Formatted list of champions and teams")
flags.DEFINE_string("map", "Old Summoners Rift", "Name of league map to use.")
flags.DEFINE_bool("save_replay", True, "Whether to save a replay at the end.")
flags.DEFINE_bool("run_client", False, "Whether to run the league client or not.")
flags.DEFINE_string("agent", "random", "Which inbuilt agent to run")
flags.DEFINE_integer("max_episodes", 0, "Maximum number of episodes to run")
flags.DEFINE_integer("max_steps", 0, "Maximum number of steps to run")
flags.DEFINE_string("host", "localhost", "Host of GameServer and Redis")
flags.DEFINE_string("config_path", "./config_dirs.txt", "File containing directories of GameServer, League client respectively")
flags.DEFINE_bool("enable_cooldowns", False, "Toggles cooldowns (default is False)")
flags.DEFINE_bool("manacosts_enabled", False, "Toggles mana costs for spells (default is False)")

def main(unused_argv):
    print("COOLDOWNS ENABLED:", FLAGS.enable_cooldowns)
    print("MANACOSTS ENABLED:", FLAGS.manacosts_enabled)
    
    players = []
    agents = []

    for player in FLAGS.players.split(","):
        c, t = player.split(".")
        players.append(lol_env.Agent(champion=c, team=t))
        if FLAGS.agent == "base":
            agents.append(base_agent.BaseAgent())
        elif FLAGS.agent == "random":
            agents.append(random_agent.RandomAgent())
        elif FLAGS.agent == "scripted":
            agents.append(scripted_agent.ScriptedAgent())
    
    with lol_env.LoLEnv(
        host=FLAGS.host,
        map_name=FLAGS.map,
        players=players,
        agent_interface_format=lol_env.parse_agent_interface_format(
            feature_map=FLAGS.feature_map_size,
            feature_move_range=FLAGS.feature_move_range
        ),
        human_observer=FLAGS.run_client,
        cooldowns_enabled=FLAGS.enable_cooldowns,
        manacosts_enabled=FLAGS.manacosts_enabled,
        config_path=FLAGS.config_path) as env:

        run_loop.run_loop(agents, env, max_episodes=FLAGS.max_episodes,
                          max_steps=FLAGS.max_steps)
        if FLAGS.save_replay:
            env.save_replay(agents[0].__class__.__name__)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)