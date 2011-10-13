#!/usr/bin/env python

# this executable combines illumina and 454 py and
# is meant to be stored somewhere in PATH

# how to require lib?

import sys
import os
from lib import *
from metacram import *


def epic_fail():
    print 'epic fail'

# parse arguments
if len(sys.argv) < 2:
    epic_fail()
    
task = sys.argv[1]


{
    'illumina': run_illumina,
    '454': run_454,
}.get(task, epic_fail).__call__()