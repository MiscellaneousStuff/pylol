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
"""Helper functions for lib modules which don't belong anywhere else."""

import json

from pylol.env import lol_env

def write_config(config_path, players, map_name, cooldowns_enabled, manacosts_enabled,
                 minion_spawns_enabled):
    players = [lol_env.LoLEnvSettingsPlayer(i+1, i+1, player.champ, player.team)
               for i, player in enumerate(players)]

    settings = lol_env.LoLEnvSettings(players,
        game = lol_env.LoLEnvSettingsGame(map=lol_env.MAP[map_name]),
        gameInfo = lol_env.LoLEnvSettingsGameInfo(
            cooldowns_enabled=cooldowns_enabled,
            manacosts_enabled=manacosts_enabled,
            minion_spawns_enabled=minion_spawns_enabled))

    settings = json.dumps(settings, indent=4)

    with open(config_path + "GameInfo.json", "w") as file:
        file.write(settings)