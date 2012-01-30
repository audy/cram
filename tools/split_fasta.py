#!/usr/bin/env python

import sys

usage = "<input> <number_of_records> <output_directory>"

input = sys.argv[1]
n = int(sys.argv[2])
out_dir = sys.argv[3]

i, p = 0, 0
with open(input) as handle:
  for line in handle:
    if (i > n) or (p == 0):
      out = open("%s/%s.fna" % (out_dir, p), 'w')
      p += 1
      i = 0
    if line.startswith('>'):
      i += 1
    print >> out, line.strip()
