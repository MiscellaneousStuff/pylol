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

from pylol.agents import scripted_agent
from pylol.agents import base_agent, random_agent
from pylol.env import lol_env
from pylol.env import run_loop
from pylol.lib import point_flag

FLAGS = flags.FLAGS
point_flag.DEFINE_point("feature_map_size", "16000",
                        "Resolution for screen feature layers.")
point_flag.DEFINE_point("feature_move_range", "-4, 4",
                        "Resolution for screen feature layers.")

def main(unused_argv):
    with lol_env.LoLEnv(
        map_name="New Summoners Rift",
        players=[
            lol_env.Agent(champion="Ezreal", team="BLUE"),
            lol_env.Agent(champion="Ezreal", team="PURPLE")
        ],
        agent_interface_format=lol_env.parse_agent_interface_format(
            feature_map=FLAGS.feature_map_size,
        ),
        human_observer=False,
        cooldowns_enabled=False) as env:
        """
        scripted_agents = [
            scripted_agent.ScriptedAgent(id=1, team="BLUE", env=env._controllers[0]),
            scripted_agent.ScriptedAgent(id=2, team="PURPLE", env=env._controllers[0])
        ]
        """
        random_agents = [
            random_agent.RandomAgent()
        ]
        """
        base_agents = [
            base_agent.BaseAgent()
        ]
        """
        # episodes = 2
        steps = 100
        run_loop.run_loop(random_agents, env, max_steps=steps)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)