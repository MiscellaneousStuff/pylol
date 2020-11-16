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
"""Launch the game and set up communication."""

from absl import logging
import subprocess
import time
import os

from absl import flags

from pylol.lib import remote_controller

class LoLLaunchError(Exception):
    pass

class LoLProcess(object):
    """Launch a modified LeagueSandbox server, initialize a controller, and
    later, clean up.
    
    This is best used from run_configs, which decides which version to run,
    and where to find it.
    """

    def __init__(self, run_config, exec_path, timeout_seconds=20, full_screen=False,
                 host=None, port=None, window_size=(640, 480), **kwargs):
        """Launch the League of Legends process.

        Args:
            run_config: `run_configs.lib.RunConfig` object.
            exec_path: Path to the binary to run.
            full_screen: Whether to launch the game window full_screen.
            host: IP for the game to listen on for clients.
            port: Port GameServer should listen on for clients.
            timeout_seconds: Timeout for the GameServer to start before we give up.
            window_size: Screen size if not full screen.
        """

        self._proc = None
        self.controller = None
        self.check_exists(exec_path)
        self.host = host or "localhost"
        self.port = port or "8394"

        args = [
            exec_path,
            "--host", self.host,
            "--port", self.port
        ]

        try:
            self.controller = remote_controller.RemoteController(
                None, None, None, timeout_seconds=timeout_seconds)
            self._proc = self.launch(run_config, args, **kwargs)
        except:
            self.close()
            raise

    def launch(self, run_config, args, **kwargs):
        """Launch the process and return the process object."""
        del kwargs
        try:
            print("RUN CONFIG CWD: ", run_config.cwd)
            return subprocess.Popen(args, cwd=run_config.cwd, env=run_config.env)
        except OSError:
            logging.execution("Failed to launch")
            raise LoLLaunchError("Failed to launch: %s" % args)
    
    def close(self):
        """Shut down the game and clean up."""
        if hasattr(self, "controller") and self.controller:
            self.controller.close()
            self.controller = None
        self.shutdown()
    
    def shutdown(self):
        """Terminate the GameServer subprocess."""
        if self._proc:
            ret = shutdown_proc(self._proc, 3)
            logging.info("Shutdown with return code: %s", ret)
            self._proc = None
    
    def check_exists(self, exec_path):
        if not os.path.isfile(exec_path):
            raise RuntimeError("Trying to run: '%s', but it doesn't exist " % exec_path)
        if not os.access(exec_path, os.X_OK):
            raise RuntimeError("Trying to run: '%s', but it isn't executable" % exec_path)

def shutdown_proc(p, timeout):
    """Wait for a proc to shut down, then terminate or kill it after `timeout`."""
    freq = 10 # How often to check per second
    for _ in range(1 + timeout * freq):
        p.terminate()
        ret = p.poll()
        if ret is not None:
            logging.info("Shutdown gracefully.")
            return ret
        time.sleep(1 / freq)
    logging.warning("Killing the process.")
    p.kill()
    return p.wait()