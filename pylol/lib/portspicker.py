# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""portpicker for multiple ports.

Claude 3.5 Sonnet auto generated migration for 2025 for increased
stability."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import socket
import time
from contextlib import closing
from typing import List, Set, Optional

# The set of ports returned by pick_contiguous_unused_ports and not by
# the underlying port checking.
_contiguous_ports: Set[int] = set()

def is_port_free(port: int) -> bool:
    """Check if a port is available."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind(('localhost', port))
            return True
        except (socket.error, OSError):
            return False

def pick_unused_port() -> Optional[int]:
    """Find and return a single unused port."""
    for port in range(1024, 65535):
        if port not in _contiguous_ports and is_port_free(port):
            return port
    return None

def pick_unused_ports(num_ports: int, retry_interval_secs: float = 1, 
                     retry_attempts: int = 5) -> List[int]:
    """Reserves and returns a list of `num_ports` unused ports."""
    if num_ports <= 0:
        raise ValueError(f"Number of ports must be >= 1, got: {num_ports}")
    
    ports = set()
    for _ in range(retry_attempts):
        while len(ports) < num_ports:
            if port := pick_unused_port():
                ports.add(port)
            else:
                break
                
        if len(ports) == num_ports:
            return list(ports)
            
        # Wait before retrying
        time.sleep(retry_interval_secs)

    # Could not obtain enough ports. Release what we do have.
    return_ports(ports)
    raise RuntimeError(f"Unable to obtain {num_ports} unused ports.")

def pick_contiguous_unused_ports(num_ports: int, retry_interval_secs: float = 1,
                               retry_attempts: int = 5) -> List[int]:
    """Reserves and returns a list of `num_ports` contiguous unused ports."""
    if num_ports <= 0:
        raise ValueError(f"Number of ports must be >= 1, got: {num_ports}")

    for _ in range(retry_attempts):
        start_port = pick_unused_port()
        if start_port is not None:
            ports = [start_port + p for p in range(num_ports)]
            
            # Verify all ports in range are actually free
            if all(is_port_free(p) for p in ports[1:]):
                _contiguous_ports.update(ports[1:])
                return ports
                
        time.sleep(retry_interval_secs)

    raise RuntimeError(f"Unable to obtain {num_ports} contiguous unused ports.")

def return_ports(ports: List[int]) -> None:
    """Returns previously reserved ports so that may be reused."""
    for port in ports:
        if port in _contiguous_ports:
            _contiguous_ports.discard(port)


# """portpicker for multiple ports."""

# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function

# import time
# import portpicker

# # The set of ports returned by pick_contiguous_unused_ports and not by
# # the underlying portpicker.
# _contiguous_ports = set()


# def pick_unused_ports(num_ports, retry_interval_secs=1, retry_attempts=5):
#   """Reserves and returns a list of `num_ports` unused ports."""
#   if num_ports <= 0:
#     raise ValueError("Number of ports, must be >= 1, got: %s" % num_ports)
#   ports = set()
#   for _ in range(retry_attempts):
#     ports.update(
#         portpicker.pick_unused_port() for _ in range(num_ports - len(ports)))
#     ports.discard(None)  # portpicker returns None on error.
#     if len(ports) == num_ports:
#       return list(ports)
#     # Duplicate ports can be returned, especially when insufficient ports are
#     # free. Wait for more ports to be freed and retry.
#     time.sleep(retry_interval_secs)

#   # Could not obtain enough ports. Release what we do have.
#   return_ports(ports)

#   raise RuntimeError("Unable to obtain %d unused ports." % num_ports)


# def pick_contiguous_unused_ports(
#     num_ports,
#     retry_interval_secs=1,
#     retry_attempts=5):
#   """Reserves and returns a list of `num_ports` contiguous unused ports."""
#   if num_ports <= 0:
#     raise ValueError("Number of ports, must be >= 1, got: %s" % num_ports)
#   for _ in range(retry_attempts):
#     start_port = portpicker.pick_unused_port()
#     if start_port is not None:
#       ports = [start_port + p for p in range(num_ports)]
#       if all(portpicker.is_port_free(p) for p in ports):
#         _contiguous_ports.update(ports[1:])
#         return ports
#       else:
#         portpicker.return_port(start_port)

#     time.sleep(retry_interval_secs)

#   raise RuntimeError("Unable to obtain %d contiguous unused ports." % num_ports)


# def return_ports(ports):
#   """Returns previously reserved ports so that may be reused."""
#   for port in ports:
#     if port in _contiguous_ports:
#       _contiguous_ports.discard(port)
#     else:
#       portpicker.return_port(port)
