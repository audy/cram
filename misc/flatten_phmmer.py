#!/usr/bin/env python

# PHMMER does not let you report only the best hit.
# I have 11GB Phmmer files :(

# Austin


import sys

lastquery = False

with open(sys.argv[1]) as handle:
    for line in handle:
        if line.startswith('#'):
            print line.strip()
            continue
        line = line.split()
        query = line[2]
        if lastquery and query != lastquery:
            print ' '.join(line)
        lastquery = query

