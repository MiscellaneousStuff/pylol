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
"""Watch a replay which was made using pylol using the league client."""

from configparser import ConfigParser

from pylol.lib import lol_process
from pylol import run_configs
from pylol.env import lol_env
from pylol.lib import portspicker
from pylol.lib import replay

from absl import flags
from absl import app

flags.DEFINE_string("replay_path", "", "Path to the replay file")
flags.DEFINE_string("config_path", "./config.txt", "File containing directories of GameServer, League client respectively")
flags.DEFINE_string("host", "localhost", "Host for GameServer and league client")
flags.DEFINE_string("players", "Ezreal.BLUE,Ezreal.PURPLE", "NOTE: TEMPORARY")

FLAGS = flags.FLAGS

def main(unused_argv):
    try:
        with open(FLAGS.config_path) as f:
            cfg = ConfigParser()
            cfg.read_string(f.read())
            game_server_dir = cfg.get("dirs", "gameserver")
            client_dir = cfg.get("dirs", "lolclient")
    except:
        raise IOError("Could not open config file: '%s'" % FLAGS.config_path)

    try:
        with open(FLAGS.replay_path) as f:
            replay_info = replay.get_replay_info(f.read())
    except:
        raise IOError("Could not open replay file: '%s'" % FLAGS.config_path)

    try:
        run_config = run_configs.get(game_server_dir=game_server_dir)
        ports = portspicker.pick_contiguous_unused_ports(2)
        client_port = ports[0]
        redis_port = ports[1]
        with run_config.start(replay_path=FLAGS.replay_path,
                                host=FLAGS.host,
                                human_observer=True,
                                players=replay_info["players"],
                                multiplier=replay_info["multiplier"],
                                step_multiplier=1,
                                client_port=client_port,
                                redis_port=redis_port,
                                client_dir=client_dir,
                                map_name=replay_info["map"],
                                cooldowns_enabled=False,
                                manacosts_enabled=False,
                                minion_spawns_enabled=False) as controller:
            controller.connect()
            for _ in range(replay_info["action_count"]):
                controller.observe()
    except KeyboardInterrupt:
        pass

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)