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
from pylol.agents import base_agent, random_agent
from pylol.env import lol_env
from pylol.env import run_loop

if __name__ == "__main__":
    with lol_env.LoLEnv(
        map_name="New Summoners Rift",
        players=[lol_env.Agent(champion="Ezreal", team="BLUE")]) as env:
        scripted_agents = [
            scripted_agent.ScriptedAgent(name="1", id=1, champ="Ezreal",
                team="BLUE", env=env._controllers[0])
        ]
        random_agents = [
            random_agent.RandomAgent()
        ]
        base_agents = [
            base_agent.BaseAgent()
        ]
        episodes = 1
        steps = 100
        run_loop.run_loop(random_agents, env, max_steps=steps)