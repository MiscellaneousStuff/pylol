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

# from absl import flags

from pylol.lib import lol_process
from pylol.run_configs import platforms
from pylol.run_configs import lib

"""
flags.DEFINE_string("lol_run_config", None,
                    "Which run_config to use to spawn the binary.")
FLAGS = flags.FLAGS
"""

def get():
    """Get the config chosen by flags."""
    configs = {c.name(): c
        for c in lib.RunConfig.all_subclasses() if c.priority()}
    
    if not configs:
        raise lol_process.LoLLaunchError("No valid run_configs found.")
    
    # if FLAGS.lol_run_config is None:
    return max(configs.values(), key=lambda c: c.priority())

    """
    try:
        return configs[FLAGS.lol_run_config]
    except KeyError:
        lol_process.LoLLaunchError(
        "Invalid run_config. Valid configs are: %s" % (
            ", ".join(sorted(configs.keys()))))
    """