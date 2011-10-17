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
      handle.next()
      for line in handle:
            c, n = line.strip().split(SEP)

            assert c not in datas[fn] # sum?
            datas[fn][c] = n


# print out as a tsv file
all_keys = set()
[all_keys.update(i.keys()) for i in datas.values()]

vals = sorted(list(set(i for i in all_keys)))

header = sorted(datas.keys())
print "CATEGORY\t%s" % "\t".join(header)

for c in vals:
    print "%s" % c,
    for h in header:
        n = datas[h].get(c, 'X')
        print "\t%s" % (n),
    print ''
