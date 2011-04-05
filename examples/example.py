#!/usr/bin/env python
"""Example plugin for NagiosPlugin class."""

import sys

from NagiosPlugin import NagiosPlugin

n = NagiosPlugin("An example check")
argparser = n.defaultArgs()
try:
    args = argparser.parse_args(sys.argv[1:])

    # Check something
    def checkSomething():
        return 5

    res = checkSomething()

    messages = { 
        n.CRITICAL: "Something gone wild.",
        n.WARNING: "Something getting out of bounds.",
        n.OK: "Everything fine."
        }

    stat = n.CRITICAL * args.critical[0](res)
    stat = stat or n.WARNING * args.warning[0](res)

    out = n.format([(stat, messages[stat])])
except Exception as Err:
    out = n.format([(n.UNKNOWN, Err[-1])])

n.exit(*out)
