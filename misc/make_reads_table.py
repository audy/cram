#!/usr/bin/env python
#encoding: utf-8

# I really need to be using a DB at this point :(

# count num for all SSs in T

import sys

# The part you can edit
from pprint import pprint

filenames = {
    # 'Filename': 'header',
    'case1.txt': 'case1',
    'case2.txt': 'case2',
    'case3.txt': 'case3',
    'case4.txt': 'case4',
    'cont1.txt': 'cont1',
    'cont2.txt': 'cont2',
    'cont3.txt': 'cont3',
    'cont4.txt': 'cont4'
}

ffilenames = {
    't1': 't1',
    't2': 't2'
}

from collections import defaultdict

# Load Subsystem Hierarchies
with open('subsystems2role') as handle:
    gene_to_subsystems = defaultdict(set)
    for line in handle:
        line = [ i.strip() for i in line.split('\t') ]
        l = [ line[2], line[0], line[1] , line[3] ]
        n = []
        for i in range(len(l)):
            n.append(l[i])
            lin = ';'.join(n)
            gene_to_subsystems[line[3]].add(lin)

# Count it
file_ss_count = {}
for filename in filenames:
    head = filenames[filename]
    with open(filename) as handle:
        for line in handle:
            count, name = [ i.strip() for i in line.split() ][:2]
            for lin in gene_to_subsystems[name]:
                try:
                    file_ss_count[lin]
                except KeyError:
                    file_ss_count[lin] = {}
                    
                try:
                    file_ss_count[lin][head] += int(count)
                except KeyError:
                    file_ss_count[lin][head] = int(count)


headers = sorted(filenames.values())
print '# %s' % '\t'.join([i for i in headers])
for lin in file_ss_count:
    for head in headers:
        try:
            print '%s\t' % file_ss_count[lin][head],
        except KeyError:
            print '0\t',
    print '\t%s' % lin
