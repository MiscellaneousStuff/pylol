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

def run_loop(agents, env, max_steps=0, max_episodes=0):
    # Re-define env for now
    env = env._controllers[0]
    env.connect()

    # Execute GameServer
    """
    start_time = time.perf_counter()
    client_load = None
    # run_config = run_configs.get()
    # GameServerConsole = lol_process.LoLProcess(run_config, "/mnt/c/Users/win8t/Desktop/AlphaLoL_AI/GameServerTest/LeagueSandbox-RL-Learning/GameServerConsole/bin/Debug/netcoreapp3.0/")
    """

    """
    GameServerConsoleArgs = [
        "./GameServerConsole",
        "--human_count",
        "1", # str(args.human_count),
        "--agent_count",
        "1", # str(args.agent_count)
    ]
    GameServerConsole = subprocess.Popen(GameServerConsoleArgs, stdout=subprocess.PIPE, cwd="/mnt/c/Users/win8t/Desktop/AlphaLoL_AI/GameServerTest/LeagueSandbox-RL-Learning/GameServerConsole/bin/Debug/netcoreapp3.0/")
    """

    """ # Start Client by waiting for "Game is ready" in GameServerConsole output
    # GameServerConsole = lol_process.LoLProcess(run_config, "/mnt/c/Users/win8t/Desktop/AlphaLoL_AI/GameServerTest/LeagueSandbox-RL-Learning/GameServerConsole/bin/Debug/netcoreapp3.0/")
    LeagueOfLegendsClient = None
    while True:
        output = str(GameServerConsole.stdout.readline())
        # print(output)
        if "Game is ready" in output:
            if True: # if args.human_count > 0:
                # Automatically start the client when ready
                client_load = time.perf_counter()
                LeagueOfLegendsClientArgs = [
                    "./League of Legends.exe",
                    "8394",
                    "../../../../../../LoLLauncher.exe",
                    "",
                    "127.0.0.1 5119 17BLOhi6KZsTtldTsizvHg== 1"
                ]
                LeagueOfLegendsClient = subprocess.Popen(LeagueOfLegendsClientArgs, stdout=subprocess.DEVNULL, cwd="/mnt/c/LeagueSandbox/League_Sandbox_Client/RADS/solutions/lol_game_client_sln/releases/0.0.1.68/deploy/")
            break
        else:
            if time.perf_counter() - start_time >= 10:
                print("GameServer timed out")
                # os.system("killall -9 GameServerConsole")
                GameServerConsole.kill()
                LeagueOfLegendsClient.kill()
                sys.exit()
    
    while time.perf_counter() < client_load + 20.0:
        pass
    """

    # Loop variables
    total_episodes = 0
    start_time = time.time()
    steps = 0

    # This won't be needed in the future
    for agent in agents:
        agent.env = env

    # Observation and action spec
    """
    observation_spec = env.observation_spec()
    action_spec = env.action_spec()
    for agent, obs_spec, act_spec in zip(agents, observation_spec, action_spec):
        agent.setup(obs_spec, act_spec)
    """

    try:
        while not max_episodes or total_episodes < max_episodes:
            # Waits 1 second for an observation from the GameServer
            # If none are found, quit
            obs_list = []
            for agent in agents:
                obs = env.observe()
                if obs == None:
                    print("KILLING PROCESS: ")
                    os.system("killall -9 GameServerConsole")
                    os.system("killall -9 redis-server")
                    sys.exit()
                obs_list.append(obs)
            
            # Do initialization after observation (because observation initialization embedded within every observation)
            if steps == 0:
                env.players_reset()
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
            if env.someone_died(obs_list[0]) and len(agents[0].state_action_buffer) > 4:

                # Update agents
                for agent in agents:
                    agent.store_episode()
                
                # Reset both players by reviving them
                env.players_reset()

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
def run_loop(agents, env, max_episodes=0):
    # A run loop for agent/environment interaction
    total_episodes = 0
    start_time = time.time()

    observation_spec = env.observation_spec()
    action_spec = env.action_spec()
    for agent, obs_spec, act_spec in zip(agents, observation_spec, action_spec):
        agent.setup(obs_spec, act_spec)
    try:
        while total_episodes < max_episodes:
            total_episodes += 1
            actions = [agent.step(timestep)
                       for agent, timestep in zip(agents, timesteps)]
            if max_frames and total_frames >= max_frames:
                return
            if timesteps[0].last():
                break
            timesteps = env.step(actions)
    except KeyboardInterrupt:
        pass
    finally:
        elapsed_time = time.time() - start_time
        print("Took %.3f seconds for %s steps: %.3f fps" % (
            elapsed_time, steps, steps / elapsed_time))
"""