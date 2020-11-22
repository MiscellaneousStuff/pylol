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
"""Replay a PyLoL agent-only recorded game."""

import sys
import json
import time

from absl import app
from absl import flags

from pylol import maps
from pylol import run_configs
from pylol.env import lol_env
from pylol.lib import point_flag
from pylol.agents import base_agent

FLAGS = flags.FLAGS

point_flag.DEFINE_point("feature_map_size", "16000",
                        "Resolution for screen feature layers.")
point_flag.DEFINE_point("feature_move_range", "8",
                        "Resolution for screen feature layers.")
flags.DEFINE_string("replay", "", "Name of the replay to show.")
flags.DEFINE_bool("run_client", False, "Replay the game using the client")

def main(unused_argv):
    """Run LoL to replay a game."""
    if (FLAGS.replay and not FLAGS.replay.lower().endswith("json")):
        sys.exit("Must supply a replay ending in .json.")

    replay_path = "/mnt/c/Users/win8t/Desktop/AlphaLoL_AI/GameServerTest/LeagueSandbox-RL-Learning/GameServerConsole/bin/Debug/netcoreapp3.0/Replays/RandomAgent/"
    replay_path += FLAGS.replay

    replay_json = ""
    with open(replay_path) as f:
        replay_json = json.loads(f.read())

    info    = replay_json["info"]
    actions = replay_json["actions"]

    steps = len(set([action["game_time"] for action in actions]))
    all_steps = len([action["game_time"] for action in actions])

    run_config = run_configs.get()
    exec_path = ""

    map_name = info["map"]
    players = info["players"].split(",")
    players = [[player.split(".")[0], player.split(".")[1]]
                for player in players]
    players = [lol_env.Agent(champion=champ, team=team)
               for champ, team in players]

    action_groups = []
    last_game_time = actions[0]["game_time"]
    current_group = []
    for action in actions:
        if action["game_time"] != last_game_time:
            action_groups.append(current_group)
            current_group = []
        current_group.append(action)
    action_groups = action_groups[1:]

    #print("PLAYERS:", players)
    #print("STEPS, ALL STEPS:", steps, all_steps)
    #print("ACTIONS", actions)
    #print("ACTION GROUPS:", action_groups)

    with run_config.start(
            human_observer=False,
            players=players,
            map_name=map_name,
            cooldowns_enabled=False) as controller:
        
        # info = controller.replay_info(replay_json)

        controller.connect()

        max_steps = all_steps
        steps = 0

        start_time = time.time()
        
        # Group actions occuring at the same time together

        try:
            for i in range(len(action_groups)):
                for player in players:
                    controller.observe()
                for action in action_groups[i]:
                    print("\n\n")
                    print(action_groups[i][0]["game_time"])
                    controller.send_raw_action(action)
        except KeyboardInterrupt:
            pass
        finally:
            elapsed_time = time.time() - start_time
            print("Took %.3f seconds for %s steps: %.3f fps" % (
                elapsed_time, steps, steps / elapsed_time))

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)