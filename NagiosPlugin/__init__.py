#!/usr/bin/env python
"""Provide a Nagios Plugin base class that can be used to evaluate ranges and 
format results."""

import sys
import re

import argparse

__author__ = "Jonathan Villemaire-Krajden <jonvk@evolvingweb.ca>"
__copyright__ = "Copyright 2011, Evolving Web Inc."
__licence__ = "GPL v3"
__version__ = "0.1"

class NagiosRangeException(Exception):
    """Exception raised when the range argument is invalid."""
    pass

class NagiosPlugin:
    "Provides default Nagios plugin development tools."
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3
    statusMessages = {
        OK: "OK",
        WARNING: "WARNING",
        CRITICAL: "CRITICAL",
        UNKNOWN: "UNKNOWN"
        }

    def __init__(self, description=""):
        "Set plugin description."
        self.description = description

    def defaultArgs(self):
        """Set the default arguments which must be implemented by well behaved 
        plugins"""
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('-t', '--timeout')
        parser.add_argument('-w', '--warning', type=self.parseRange)
        parser.add_argument('-c', '--critical', type=self.parseRange)
        parser.add_argument('-H', '--hostname')
        parser.add_argument('-V', '--version', help='print version')
        parser.add_argument('-v', '--verbose', help='verbose output')
        return parser

    def parseRange(self, nrange):
        """Parse range according to Nagios plugin syntax.
        
        see http://nagiosplug.sourceforge.net/developer-guidelines.html#THRESHOLDFORMAT
        Returns a tuple (lt, gt, draw_val)
		This tuple can be passed to checkVal to check whether the status is critical or not.
		draw_val is for the performance output, and will only be set if we have a simple value for the range.
        
        Example: 
            >>> parseRange("5:10")
            (5, 10, False)

        """
        inf = float('inf')
        nan = float('nan')
        # 5

        val = re.match('(\d+\.?\d*)$', nrange)
        if val:
            minval = float(val.groups()[0])
            return (0, minval, minval)
        # 5:
        val = re.match('(\d+\.?\d*):$', nrange)
        if val:
            minval = float(val.groups()[0])
            return (minval, inf, minval)
        # ~:5
        val = re.match('~:(\d+\.?\d*)$', nrange)
        if val:
            maxval = float(val.groups()[0])
            return (-inf, maxval, maxval)
        # 10:20
        val = re.match('(\d+\.?\d*):(\d+\.?\d*)$', nrange)
        if val:
            minval = float(val.groups()[0])
            maxval = float(val.groups()[1])
            return (minval, maxval, nan)
        # @10:20
        val = re.match('@(\d+\.?\d*):(\d+\.?\d*)$', nrange)
        if val:
            minval = float(val.groups()[0])
            maxval = float(val.groups()[1])
            return (maxval, minval, nan)
        raise NagiosRangeException("Invalid range: %s" %nrange)
    
    def checkVal(self, val, nrange):
        """Return true if the value is within the range, eg non critical, false otherwise.

        nrange should be a range such as output by parseRange().

"""
        low, high = nrange[0:2]
        return not (val < low or val > high)

    def format(self, results):
        """Returns an exit status and a formatted output string.
        Input: results : list of tuples containing:
          (status: OK, WARN, CRITICAL, UNKNOWN,
          message,
          perfdata - optional
          )

        The messages for results with the worst severity will be concatenated,
        the performance data will all be concatenated.

        Return:
        (STATUS, OUTPUT)
        """
        status = NagiosPlugin.OK
        messages = []
        perf = []
        for result in results:
            if len(result) == 3:
                perf.append(result[2])
            # Don't append empty strings
            if result[0] == status and result[1]:
                messages.append(result[1])
            elif result[0] > status:
                messages = [result[1]]
                status = result[0]
        message = NagiosPlugin.statusMessages[status] + ' - ' + "; ".join(messages)
        if perf:
            perf = " ".join(filter(lambda x: x, perf))
            message += " | " + perf
        return (status, message)

    def exit(self, status, message):
        "Print the message and exit with status code."
        print message
        sys.exit(status)
