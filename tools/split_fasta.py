#!/usr/bin/env python

import sys
import os
from metacram import dnaio
from itertools import count

usage = "%s <num_records_per_file> <qseq, fastq, or fasta> <file> <out_dir>" % (os.path.basename(__file__))

try:
    num_records_per_file = int(sys.argv[1])
    filename = sys.argv[2]
    filetype = sys.argv[3]
    out_dir = sys.argv[4]
except:
    print >> sys.stderr, usage
    quit(-1)

counter = count(0)
file_number = 0
with dnaio.Dna(open(filename), type=filetype) as records:
    for record in records:
        n = counter.next()
        if n >> num_records_per_file:
            counter = count(0)
            out_handle = open('%s/%s.%s' % (out_dir, file_number, file_type))
