#!/usr/bin/env python
# -*- coding:utf-8 -*-


import sys
import argparse
import collections

from functools import wraps

import logging

# We are assuming, that there is an already configured logger present
logger = logging.getLogger(__name__)


class CommandLine:
    """Create a command line interface for the application.
    Can call any core method as action.

    Careful: The function defintion order is reflected in the cli.
    Can be reorder using the *weight* flag of the initializer.
    'lighter' Arguments will go first
    """

    arguments = collections.OrderedDict()

    @classmethod
    def handle(self, core, name):
        """Handle the command line arguments.
        Returns true if the gui is to be shown, this is controlled
        through the 'batch' argument."""
        call_buckets = collections.defaultdict(list)
        # Build the ArgumentParser
        arg_parser = argparse.ArgumentParser(name)
        for name, arg in self.arguments.items():
            arg_name = f"--{name}"
            arg_opts = {"default": arg.default, "action": arg.action, "help": arg.help}
            arg_opts["nargs"] = len(arg.args) if len(arg.args) > 0 else None
            if arg.action == "store":
                arg_opts["metavar"] = arg.args
                arg_opts["type"] = arg.type
            arg_parser.add_argument(arg_name, **arg_opts)
            call_buckets[arg.weight].append(arg)
        # Add batch argument to suppress gui
        arg_parser.add_argument(
            "--batch",
            "-b",
            "--no-gui",
            help="Run in batch mode (Don't show the gui)",
            action="store_true",
            default=sys.flags.interactive,
        )
        # Parse all arguments
        args = arg_parser.parse_args()
        # Check all actions
        call_order = sorted(call_buckets.keys())
        for weight in call_order:
            for arg in call_buckets[weight]:
                params = getattr(args, arg.name.replace("-", "_"))
                if params is None:
                    continue
                if arg.owner is None:
                    arg.method(core, *params)
                elif arg.owner[0] == "View":
                    method = getattr(core.view[arg.owner[1]], arg.method_name)
                    method(*params)
                else:
                    raise TypeError("Unknown Owner")

    def __init__(self, name, *args, **flags):
        """The constructor for the CommandLine object.
        Accepts the same flags as the add_argument function of the
        ArgumentParser class.
        The *weight* flag can be used to reorder the execution of
        arguments. 'lighter' commands will go first."""
        self.name = name
        self.args = args
        self.help = flags.get("help", "")
        self.type = flags.get("type", str)
        self.default = flags.get("default", None)
        self.action = flags.get("action", "store")
        self.weight = flags.get("weight", 0)
        if self.name in CommandLine.arguments:
            raise KeyError(self.name)
        CommandLine.arguments[self.name] = self
        self.owner = flags.get("owner")

    def __call__(self, func):
        if self.help == "":
            self.help = func.__doc__
        self.method_name = func.__name__
        self.method = func

        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            return func(instance, *args, **kwargs)

        return wrapper

    def __str__(self):
        return "--{} -> {}('{}')".format(self.name, self.method, "', '".join(self.args))

    __repr__ = __str__
