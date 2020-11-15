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
"""Define the static list of types and actions for League of Legends v4.20."""

import collections
import numbers

import enum
import numpy
from pylol.lib import point
import six

def no_op(action, action_space):
    del action, action_space

def raw_no_op(action):
    del action

def numpy_to_python(val):
    """Convert numpy types to their corresponding python types."""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, six.string_types):
        return val
    if (isinstance(val, numpy.number) or
        isinstance(val, numpy.ndarray) and not val.shape):  # numpy.array(1)
        return val.item()
    if isinstance(val, (list, tuple, numpy.ndarray)):
        return [numpy_to_python(v) for v in val]
    raise ValueError("Unknown value. Type: %s, repr: %s" % (type(val), repr(val)))

class ArgumentType(collections.namedtuple(
    "ArgumentType", ["id", "name", "sizes", "fn", "values", "count"])):
    """Represents a single argument type.

    Attributes:
        id: The argument id. This is unique.
        name: The name of the argument, also unique.
        sizes: The max + 1 of each of the dimensions this argument takes.
    """

class Functions(object):
    """Represents the full set of functions.

    Can't use namedtuple since python3 has a limit of 255 function arguments, so
    build something similar.
    """

    def __init__(self, functions):
        functions = sorted(functions, key=lambda f: f.id)
        self.func_list = functions
        self.func_dict = {f.name: f for f in functions}
        if len(self.func_dict != len(self.func_list)):
            raise ValueError("Function names must be unique.")
    
    def __getattr__(self, name):
        return self._func_dict[name]

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            return self._func_list[key]
        return self._func_dict[key]

    def __getstate__(self):
        return self._func_list

    def __setstate__(self, functions):
        self.__init__(functions)

    def __iter__(self):
        return iter(self._func_list)

    def __len__(self):
        return len(self._func_list)

    def __eq__(self, other):
        return self._func_list == other._func_list

class FunctionCall(collections.namedtuple(
    "FunctionCall", ["function", "arguments"])):
    """Represents a function call action.

    Attributes:
        function: Store the function id.
        arguments: The list of arguments for that function, each being a list of
            ints.
    """
    __slots__ = ()

    @classmethod
    def init_with_validation(cls, function, arguments, raw=False):
        """Return a `FunctionCall` given some validation for the function and args.

        Args:
            function: A function name or id, to be converted into a function id enum.
            arguments: An iterable of function arguments. Arguments that are enum
                types can be passed by name. Arguments that only take on value (ie
                not a point) don't neeed to be wrapped in a list.
            raw: Whether this is a raw function call.

        Returns:
            A new `FunctionCall` instance.
        
        Raises:
            KeyError: if the enum doesn't exist.
            ValueError: if the enum id doesn't exist.
        """
        func = FUNCTIONS[function]
        args = []
        for arg, arg_type in zip(arguments, func.args):
            arg = numpy_to_python(arg)
            if arg_type.values: # Allow enum values by name or int.
                if isinstance(arg, six.string_types):
                    try:
                        args.append([arg_type.values[arg]])
                    except KeyError:
                        raise KeyError("Unknown argument value: %s, valid values: %s" % (
                            arg, [v.name for v in arg_type.values]))
                else:
                    if isinstance(arg, list):
                        arg = arg[0]
                    try:
                        args.append([arg_type.values[arg]])
                    except ValueError:
                        raise ValueError("Unknown argument value: %s, valid values: %s" % (
                arg, list(arg_type.values)))
            elif isinstance(arg, int): # Allow bare ints
                args.append([arg])
            elif isinstance(arg, list):
                args.append(arg)
            else:
                raise ValueError(
                    "Unknown argument value type: %s, expected int or list of ints, or "
                    "their numpy equivalents. Value: %s" % (type(arg), arg))
        return cls(func.id, args)