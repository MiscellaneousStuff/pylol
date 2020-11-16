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

from pylol.agents import scripted_agent
from pylol.env import lol_env
from pylol.env import run_loop
from pylol.env.lol_env import LoLEnvSettingsPlayer

if __name__ == "__main__":
    with lol_env.LoLEnv(
        map_name="Old Summoners Rift",
        players=[lol_env.Agent(champion="Ezreal", team="BLUE"),
                 lol_env.Agent(champion="Ezreal", team="PURPLE")]) as env:
        agents = [
            scripted_agent.ScriptedAgent(name="1", id=1, champ="Ezreal",
                team="BLUE", env=env._controllers[0]),
            scripted_agent.ScriptedAgent(name="2", id=2, champ="Ezreal",
                team="PURPLE", env=env._controllers[0])
        ]
        episodes = 2
        run_loop.run_loop(agents, env, max_episodes=episodes)