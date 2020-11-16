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
"""Run an agent."""

import threading

from absl import app
from absl import flags

from pylol import maps
from pylol.env import available_actions_printer
from pylol.env import run_loop
from pylol.env import lol_env

max_agent_steps = 1000000
max_episodes = 1000000
cur_map = "Old Summoners Rift"

def run_thread(agent_classes, players, map_name):
    """Run on thread worth of the environment with agents."""
    with lol_env.LoLEnv(
        map_name=map_name,
        players=players) as env:
        env = available_actions_printer.AvailableActionsPrinter(env)
        agents = [agent_cls() for agent_cls in agent_classes]
        run_loop.run_loop(agents, env, max_agent_steps, max_episodes)

def main(unused_argv):
    """Run an agent."""
    map_inst = maps.get(cur_map)

    agent_classes = []
    players = []

    threads
    for _ in range(parallel - 1):
        t = threading.Thread(target=run_thread,
                            args=(agent_classes, players, cur_map))
        threads.append(t)
        t.start()

    run_thread(agent_classes, players, cur_map)

    for t in threads:
        t.join()

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)