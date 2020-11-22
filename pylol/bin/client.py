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
flags.DEFINE_string("players", "Ezreal.BLUE,Lucian.PURPLE", "Formatted list of champions and teams")
flags.DEFINE_string("map", "Old Summoners Rift", "Name of league map to use.")
flags.DEFINE_bool("save_replay", True, "Whether to save a replay at the end.")
flags.DEFINE_bool("run_client", False, "Whether to run the league client or not.")

def main(unused_argv):
    players = []
    agents = []

    for player in FLAGS.players.split(","):
        c, t = player.split(".")
        players.append(lol_env.Agent(champion=c, team=t))
        agents.append(random_agent.RandomAgent())
    
    with lol_env.LoLEnv(
        map_name=FLAGS.map,
        players=players,
        agent_interface_format=lol_env.parse_agent_interface_format(
            feature_map=FLAGS.feature_map_size,
            feature_move_range=FLAGS.feature_move_range
        ),
        human_observer=FLAGS.run_client,
        cooldowns_enabled=False) as env:

        # episodes = 2
        steps = 50
        run_loop.run_loop(agents, env, max_steps=steps)
        if FLAGS.save_replay:
            env.save_replay(agents[0].__class__.__name__)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)