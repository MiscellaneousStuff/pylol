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
"""A run loop for agent/environment interaction."""

import time
import os
import sys
import subprocess

from pylol import run_configs

"""
def run_loop(agents, env, max_steps=0, max_episodes=0):
    # Re-define env for now
    controller = env._controllers[0]
    controller.connect()

    # Loop variables
    total_episodes = 0
    start_time = time.time()
    steps = 0

    # This won't be needed in the future
    for agent in agents:
        agent.env = controller

    # Observation and action spec
    observation_spec = env.observation_spec()
    action_spec = env.action_spec()
    print("OBS, ACT SPECS:", observation_spec, action_spec)
    for agent, obs_spec, act_spec in zip(agents, observation_spec, action_spec):
        agent.setup(obs_spec, act_spec)

    try:
        while not max_episodes or total_episodes < max_episodes:
            # Waits 1 second for an observation from the GameServer
            # If none are found, quit
            obs_list = []
            for agent in agents:
                obs = controller.observe()
                if obs == None:
                    sys.exit()
                obs_list.append(obs["observation"])
            
            # Do initialization after observation (because observation initialization embedded within every observation)
            if steps == 0:
                controller.players_reset()
                for agent in agents:
                    agent.reset()

            # Print game time
            print(obs_list[0]["game_time"])

            # Agents react to observation
            for obs, agent in zip(obs_list, agents):
                agent.step(obs)
            steps += 1

            # Break if we've reached the max steps
            if max_steps and steps >= max_steps:
                return
            
            # If someone has died, the episode has finished
            if controller.someone_died(obs_list[0]) and len(agents[0].state_action_buffer) > 4:

                # Update agents
                for agent in agents:
                    agent.store_episode()
                
                # Reset both players by reviving them
                controller.players_reset()

                # Re-teleport them
                for agent in agents:
                    agent.reset()
                
                # Increment episode
                total_episodes += 1

    except KeyboardInterrupt:
        pass

    finally:
        elapsed_time = time.time() - start_time
        print("Took %.3f seconds for %s steps: %.3f fps" % (
            elapsed_time, steps, steps / elapsed_time))
"""


def run_loop(agents, env, max_steps=0, max_episodes=0):
    # Connect
    controller = env._controllers[0]
    controller.connect()

    # A run loop for agent/environment interaction
    total_episodes = 0
    steps = 0
    start_time = time.time()

    observation_spec = env.observation_spec()
    action_spec = env.action_spec()
    for agent, obs_spec, act_spec in zip(agents, observation_spec, action_spec):
        agent.setup(obs_spec, act_spec)
    try:
        while not max_episodes or total_episodes < max_episodes:
            total_episodes += 1
            timesteps = env.reset()
            for a in agents:
                a.reset()
            while True:
                steps += 1
                print("STEP:", steps)
                actions = [agent.step(timestep)
                           for agent, timestep in zip(agents, timesteps)]
                if max_steps and steps >= max_steps:
                    return
                """
                if timesteps[0].last():
                    break
                """
                print("STEP TIMESTEPS:", steps)
                timesteps = env.step(actions)
    except KeyboardInterrupt:
        pass
    finally:
        elapsed_time = time.time() - start_time
        print("Took %.3f seconds for %s steps: %.3f fps" % (
            elapsed_time, steps, steps / elapsed_time))