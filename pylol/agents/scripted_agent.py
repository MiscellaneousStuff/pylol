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
"""Hardcoded scripted agent."""

from random import randint

# Rewards
REWARD_WEIGHT = {
    "death": -3.0,
    "dealing_dmg": +0.4,
    "taking_dmg": -0.4,
    "timestep_elapsed": -0.001, # unset for now, probably not needed
    "kill": +3.0
}

# Agent
class ScriptedAgent:
    def __init__(self, name, id, champ, team, lolenv):
        # Game data
        self.name = name
        self.id = id
        self.champ = champ
        self.team = team
        self.lolenv = lolenv

        # Meta Data
        self.rewards = []
        self.steps = 0
        self.episodes = 0

        # ML data
        self.state_action_buffer = [] # current ep => (state, action, reward)
        self.experience = [] # (state, action, reward) / episode episode
        self.performance = [] # sum of experience rewards / episode
        self.mean_performance = [] # mean of experience rewards / episode

    # returns rewards for current episode (regardless if they've been calculated or not)
    def get_current_rewards(self):
        return list(map(lambda x: x[2], self.state_action_buffer))

    # store current episode experience and performance
    def store_episode(self):
        # print("(S, A) Buffer:", len(self.state_action_buffer[-1]), self.state_action_buffer[-1])
        rewards = list(map(lambda x: x[2], self.state_action_buffer))
        # print("REWARDS:", rewards)
        self.experience.append(self.state_action_buffer)
        self.performance.append(sum(rewards))
        self.mean_performance.append(sum(rewards) / len(rewards))
        self.state_action_buffer = []

    # update function
    # this is a trivial learning algorithm partly inspired by q-learning
    # ... but adapted for a continous control task like league of legends
    def update(self, start=0, end=None):
        
        # Update rewards based on selected experience
        experience_window = self.state_action_buffer[start:end]
        # print("(START INDEX, END INDEX, XP WINDOW VS SA BUFFER):", start, end, len(experience_window), len(self.state_action_buffer))
        # print("XP WINDOW:", experience_window)

        # calculate rewards for individual transitions
        for i in range(len(experience_window)):

            # current state action list
            current_state_action = experience_window[i]
            reward = REWARD_WEIGHT["timestep_elapsed"]

            # if its the first one, apply default rewards only
            if start == 0:
                current_state_action[2] = reward
                continue

            # otherwise calc other rewards
            previous_state_action = self.state_action_buffer[start+i-1]

            # calc taking dmg reward
            current_hp = current_state_action[0]["champ_units"][0]["current_hp"]
            prev_hp = previous_state_action[0]["champ_units"][0]["current_hp"]
            if current_hp < prev_hp:
                reward += REWARD_WEIGHT["taking_dmg"]

            # calc dealing dmg reward
            current_enemy_hp = current_state_action[0]["champ_units"][1]["current_hp"]
            prev_enemy_hp = previous_state_action[0]["champ_units"][1]["current_hp"]
            if current_enemy_hp < prev_enemy_hp:
                reward += REWARD_WEIGHT["dealing_dmg"]

            # calc death reward
            prev_alive = previous_state_action[0]["champ_units"][0]["alive"]
            current_alive = current_state_action[0]["champ_units"][0]["alive"]
            if prev_alive == 0.0 and not current_alive == 0.0:
                reward += REWARD_WEIGHT["death"]

            # calc kill reward
            prev_enemy_alive = previous_state_action[0]["champ_units"][1]["alive"]
            current_enemy_alive = current_state_action[0]["champ_units"][1]["alive"]
            if prev_enemy_alive == 0.0 and not current_enemy_alive == 0.0:
                reward += REWARD_WEIGHT["kill"]

            # append sum of calculated rewards
            current_state_action[2] = reward

        # Return calculated rewards for current experience window for graphing
        experience_window_rewards = list(map(lambda x: x[2], experience_window))
        return experience_window_rewards

    # teleport the player on spawn
    def spawn(self, x, y):
        self.lolenv.player_teleport(self.id, x, y)

    # takes an observation from the game server, asks the game server to perform an action, records the (state, action) combo
    def act(self, observation, step):
        print("Player: " + self.team + " Act")
        # print("Champ Units:", observation["champ_units"])

        # Record State and Action
        state = observation
        action = None

        # ID of closest enemy
        enemy_id = -1
        lowest_distance = 0
        closest_enemy_unit = None
        me_unit = None
        for champ_unit in observation["champ_units"]:
            if champ_unit["my_team"] == 0.0:
                if enemy_id == -1:
                    enemy_id = champ_unit["user_id"]
                    lowest_distance = champ_unit["distance_to_me"]
                    closest_enemy_unit = champ_unit
                else:
                    if champ_unit["distance_to_me"] < lowest_distance:
                        enemy_id = champ_unit["user_id"]
                        lowest_distance = champ_unit["distance_to_me"]
                        closest_enemy_unit = champ_unit
            elif champ_unit["my_team"] == 1.0:
                if champ_unit["distance_to_me"] == 0.0:
                    me_unit = champ_unit
        closest_enemy_unit_x = closest_enemy_unit["position"]["X"]
        closest_enemy_unit_y = closest_enemy_unit["position"]["Y"]
        me_unit_x = me_unit["position"]["X"]
        me_unit_y = me_unit["position"]["Y"]
        print("Closest Enemy Position:", closest_enemy_unit_x, closest_enemy_unit_y)
        # print("ENEMY ID:", self.team, enemy_id)

        # If 
        """
        enemy_id = (self.id + AGENT_COUNT // 2) % AGENT_COUNT
        if enemy_id == 0:
            enemy_id = AGENT_COUNT
        """

        """
        # Act
        action_choice = randint(0, 5)
        if action_choice == 0: # Move
            x = randint(-4, +4)
            y = randint(-4, +4)
            action = lolenv.player_move(self.id, x, y)
        elif action_choice == 1: # Spell
            spell = 0
            action = lolenv.player_spell(self.id, 2, spell)
        elif action_choice == 2: # Noop
            action = lolenv.player_noop(self.id)
        """

        # Heal Ally if Low
        for champ_unit in observation["champ_units"]:
            if champ_unit["my_team"] == 1.0 and champ_unit["user_id"] == 1:
                if champ_unit["current_hp"] < 200:
                    action = self.lolenv.player_spell(self.id, champ_unit["user_id"], 5, me_unit_x, me_unit_y)
                    self.state_action_buffer.append([state, action, 0])
        
        """
        # If previous action was auto attack, noop
        if len(self.state_action_buffer) > 8:
            if self.state_action_buffer[-1][1]["type"] == "spell":
                action = self.lolenv.player_noop(self.id)
            elif self.state_action_buffer[-2][1]["type"] == "spell":
                # action = lolenv.player_noop(self.id)
                action = self.lolenv.player_attack(self.id, enemy_id)
            elif self.state_action_buffer[-1][1]["type"] == "attack":
                action = self.lolenv.player_noop(self.id)
            elif self.state_action_buffer[-1][1]["type"] == "move":
                x = randint(-4, 4)
                y = randint(-4, 4)
                action = self.lolenv.player_move(self.id, x, y)
            elif self.state_action_buffer[-2][1]["type"] == "move":
                choice = randint(0, 1)
                if choice == 0:
                    x = randint(-4, 4)
                    y = randint(-4, 4)
                    action = self.lolenv.player_move(self.id, x, y)
                elif choice == 1:
                    #spell = 0
                    spell = randint(0, 2)
                    # if spell == 1: spell = 2
                    if closest_enemy_unit["alive"] == 1.0:
                        action = self.lolenv.player_spell(self.id, enemy_id, spell, closest_enemy_unit_x, closest_enemy_unit_y)
                    else:
                        x = randint(-4, 4)
                        y = randint(-4, 4)
                        action = self.lolenv.player_move(self.id, x, y)
            else: #self.state_action_buffer[-1][1]["type"] == "attack":
                choice = randint(0, 1)
                if choice == 0:
                    x = randint(-4, 4)
                    y = randint(-4, 4)
                    action = self.lolenv.player_move(self.id, x, y)
                elif choice == 1:
                    #spell = 0
                    spell = randint(0, 2)
                    # if spell == 1: spell = 2
                    if closest_enemy_unit["alive"] == 1.0:
                        action = self.lolenv.player_spell(self.id, enemy_id, spell, closest_enemy_unit_x, closest_enemy_unit_y)
                    else:
                        x = randint(-4, 4)
                        y = randint(-4, 4)
                        action = self.lolenv.player_move(self.id, x, y)
        else:
            choice = randint(0, 1)
            if choice == 0:
                x = randint(-4, 4)
                y = randint(-4, 4)
                action = self.lolenv.player_move(self.id, x, y)
            elif choice == 1:
                #spell = 0
                spell = randint(0, 2)
                # if spell == 1: spell = 2
                if closest_enemy_unit["alive"] == 1.0:
                    action = self.lolenv.player_spell(self.id, enemy_id, spell, closest_enemy_unit_x, closest_enemy_unit_y)
                else:
                    x = randint(-4, 4)
                    y = randint(-4, 4)
                    action = self.lolenv.player_move(self.id, x, y)
        """

        # Spell on enemy
        # action = lolenv.player_spell(self.id, enemy_id, 0)
        # action = lolenv.player_attack(self.id, 1)
        
        # Move and Attack
        if step % 2 == 0:
            x = randint(-4, 4)
            y = randint(-4, 4)
            action = self.lolenv.player_move(self.id, x, y)
        else:
            spell = randint(0, 2)
            action = self.lolenv.player_spell(self.id, enemy_id, spell, closest_enemy_unit_x, closest_enemy_unit_y)

        # Record (State, Action)
        self.state_action_buffer.append([state, action, 0])

    def reset(self):
        if self.rewards != []:
            mean_reward = sum(self.rewards) / len(self.rewards)
            print("Episode: {}: Reward {}".format(self.episodes, mean_reward))

        if self.team == "BLUE":
            self.spawn(7500-500, 7500-500)
        elif self.team == "PURPLE":
            self.spawn(7500+500, 7500+500)
        self.steps = 0
        self.episodes += 1

    def step(self, obs):
        if self.steps == 0:
            self.act(obs, self.steps)
            self.rewards = self.update()
        else:
            self.act(obs, self.steps)
            self.rewards = self.update(self.steps-1, self.steps)
        self.steps += 1