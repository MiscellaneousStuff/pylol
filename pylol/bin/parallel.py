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
"""Run multiple games at once.

Current example runs 4 concurrent 5v5 games. Not fully tested, don't trust at this stage.
"""

import subprocess

from absl import flags
from absl import app

from pylol.lib import run_parallel

FLAGS = flags.FLAGS
flags.DEFINE_string("players", "Ezreal.BLUE,Ezreal.PURPLE", "Formatted list of champions and teams")
flags.DEFINE_string("map", "Old Summoners Rift", "Name of league map to use.")
flags.DEFINE_bool("save_replay", True, "Whether to save a replay at the end.")
flags.DEFINE_integer("count", 1, "Number of games to run at once")
flags.DEFINE_string("agent", "random", "Which inbuilt agent to run")
flags.DEFINE_integer("max_episodes", 0, "Maximum number of episodes to run")
flags.DEFINE_integer("max_steps", 0, "Maximum number of steps to run")
flags.DEFINE_string("host", "localhost", "Host of GameServer and Redis")
flags.DEFINE_string("config_path", "./config_dirs.txt", "File containing directories of gameserver, lol client and redis conf respectively")
flags.DEFINE_bool("enable_cooldowns", False, "Toggles cooldowns (default is False)")
flags.DEFINE_bool("manacosts_enabled", False, "Toggles mana costs for spells (default is False)")
flags.DEFINE_bool("minion_spawns_enabled", False, "Toggles spawning of minions (default is False")

def main(unused_argv):
    parallel = run_parallel.RunParallel()

    args = ["python3", 
    "-m", "pylol.bin.client", 
    "--players", str(FLAGS.players),
    "--map", str(FLAGS.map),
    "--save_replay", str(FLAGS.save_replay),
    "--max_steps", str(FLAGS.max_steps),
    "--max_episodes", str(FLAGS.max_episodes),
    "--agent", str(FLAGS.agent),
    "--players", str(FLAGS.players),
    "--host", str(FLAGS.host),
    "--enable_cooldowns", str(FLAGS.enable_cooldowns),
    "--manacosts_enabled", str(FLAGS.manacosts_enabled),
    "--minion_spawns_enabled", str(FLAGS.minion_spawns_enabled)]

    try:
        parallel.run((subprocess.Popen, args) for _ in range(FLAGS.count))
    except KeyboardInterrupt:
        print("CLOSE EVERYTHING :D")

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)