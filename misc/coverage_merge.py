#!/usr/bin/env python

# merge multiple coverage tables

import sys
import os

SEP = "\t"
datas = {}

# LOAD ALL THE DATAS
for f in sys.argv[1:]:
    
    fn = f
    datas[fn] = {}
    
    with open(f) as handle:
        for line in handle:
            c, n = line.strip().split(SEP)

            # assert c not in datas[fn] # sum?
            datas[fn][c] = n


# print out as a tsv file

vals = set(i for i in  datas.values()[0].keys())


header = sorted(datas.keys())

print "CATEGORY\t%s" % "\t".join(header)

for c in vals:
    print "%s" % c,
    for h in header:
        n = datas[h].get(c, '0')
        print "\t%s" % (n),
    print ''