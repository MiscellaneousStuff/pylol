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
"""A League of Legends v4.20 environment."""

import redis
import json
import subprocess

class LoLEnv():
    def __init__(self, settings, host="localhost", port=6379, db=0, timeout=1):
        self.pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.r = redis.Redis(connection_pool=self.pool)
        self.timeout = timeout
        self.running = True
        self.settings = settings

    def reset_data_streamer(self, key):
        self.r.delete(key)

    def update_data_streamer(self, key, data):
        self.r.lpush(key, json.dumps({"rewards": data}))

    # Check if someone died for this observation
    def someone_died(self, observation):
        champ_units = observation["champ_units"]
        for champ_unit in champ_units:
            if champ_unit["alive"] == 0.0:
                return True
        return False

    def start_observing(self):
        # Reset action and observation pipes
        self.r.delete("action")
        self.r.delete("observation")

        # Tell the server to start accepting actions and observations
        self.r.lpush("command", "start_observing")

    def get_observation(self):
        json_txt = self.r.brpop("observation", self.timeout)
        if json_txt == None:
            self.running = False
            print("Error: Observation timed out")
            return None
        else:
            return json.loads(json_txt[1].decode("utf-8"))
    
    def player_attack(self, player_id, target_player_id):
        action = {
            "player_id": str(player_id),
            "target_player_id": str(target_player_id)
        }
        self.r.lpush("action", "attack")
        self.r.lpush("action", json.dumps(action))
        return {"type": "attack", "data": action}

    def player_spell(self, player_id, target_player_id, spell_slot, x, y):
        action = {
            "player_id": str(player_id),
            "target_player_id": str(target_player_id),
            "spell_slot": int(spell_slot),
            "x": float(x * 1.0),
            "y": float(y * 1.0)
        }
        self.r.lpush("action", "spell")
        self.r.lpush("action", json.dumps(action))
        return {"type": "spell", "data": action}

    def players_reset(self):
        self.r.lpush("action", "reset")
        self.r.lpush("action", "")

    def player_move(self, player_id, x, y):
        action = {
            "player_id": str(player_id),
            "x": float(x * 100.0),
            "y": float(y * 100.0)
        }
        self.r.lpush("action", "move")
        self.r.lpush("action", json.dumps(action))
        return {"type": "move", "data": action}

    def player_move_to(self, player_id, x, y):
        action = {
            "player_id": str(player_id),
            "x": float(x),
            "y": float(y)
        }
        self.r.lpush("action", "move_to")
        self.r.lpush("action", json.dumps(action))

    def player_teleport(self, player_id, x, y):
        action = {
            "player_id": str(player_id),
            "x": float(x),
            "y": float(y)
        }
        self.r.lpush("action", "teleport")
        self.r.lpush("action", json.dumps(action))

    def player_noop(self, n=1):
        for i in range(n):
            self.r.lpush("action", "noop")
            self.r.lpush("action", "")
        return {"type": "noop", "data": ""}

    def player_change(self, player_id, champion_name):
        command = {
            "player_id": player_id,
            "champion_name": champion_name
        }
        self.r.lpush("command", "change_champion")
        self.r.lpush("command", json.dumps(command))

MAP = {
    "Old Summoners Rift": 1,
    "New Summoners Rift": 11,
    "Howling Abyss": 12
}

TEAM = {
    "BLUE": "BLUE",
    "PURPLE": "PURPLE"
}

SUMMONER_SPELL = {
    "FLASH": "SummonerFlash",
    "HEAL": "SummonerHeal",
    "IGNITE": "SummonerDot"
}

def LoLEnvSettingsPlayer(
    playerId,
    name,
    champion,
    team,
    rank="DIAMOND",
    skin=0,
    summoner1=SUMMONER_SPELL["FLASH"],
    summoner2=SUMMONER_SPELL["HEAL"],
    ribbon=2,
    icon=0
):
    return {
        "playerId": playerId,
        "blowfishKey": "17BLOhi6KZsTtldTsizvHg==",
        "rank": rank,
        "name": name,
        "champion": champion,
        "team": team,
        "skin": skin,
        "summoner1": summoner1,
        "summoner2": summoner2,
        "ribbon": ribbon,
        "icon": icon,
        "runes": {
            "1": 5245,
            "2": 5245,
            "3": 5245,
            "4": 5245,
            "5": 5245,
            "6": 5245,
            "7": 5245,
            "8": 5245,
            "9": 5245,
            "10": 5317,
            "11": 5317,
            "12": 5317,
            "13": 5317,
            "14": 5317,
            "15": 5317,
            "16": 5317,
            "17": 5317,
            "18": 5317,
            "19": 5289,
            "20": 5289,
            "21": 5289,
            "22": 5289,
            "23": 5289,
            "24": 5289,
            "25": 5289,
            "26": 5289,
            "27": 5289,
            "28": 5335,
            "29": 5335,
            "30": 5335
        }
    }

def LoLEnvSettingsGameInfo(
    manacosts_enabled=False,
    cooldowns_enabled=False,
    minion_spawns_enabled=False,
    cheats_enabled=True,
    is_damage_text_global=True
):
    return {
        "MANACOSTS_ENABLED":        manacosts_enabled,
        "CHEATS_ENABLED":           cheats_enabled,
        "COOLDOWNS_ENABLED":        cooldowns_enabled,
        "MINION_SPAWNS_ENABLED":    minion_spawns_enabled,
        "CONTENT_PATH": "../../../../Content",
        "IS_DAMAGE_TEXT_GLOBAL":    is_damage_text_global
    }

def LoLEnvSettingsGame(
    map=MAP["Old Summoners Rift"]
):
    return {
        "map": map,
        "dataPackage": "LeagueSandbox-Scripts"
    }

def LoLEnvSettings(players, game, gameInfo):
    return {
        "players": players,
        "game": game,
        "gameInfo": gameInfo
    }