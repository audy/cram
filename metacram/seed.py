#!/usr/bin/env python

# annotate SEED database will subsystems in headers
from metacram import dnaio
import sys

def main():
    ''' '''
    usage = 'python seed.py peg role seed > out'
    
    peg, role, seed = sys.argv[1:]
    seed_collector(peg=peg, role=role, seed=seed)

def seed_collector(**ops):
    ops['peg'] = peg
    ops['role'] = role
    ops['seed'] = seed
    ops['out'] = ops.get('out', False)
    skip_na = False

    # load subsystems from figids using subsystems2peg
    ohai("loading %s" % ops['peg'])
    figs_to_name = {}
    with open(ops['peg']) as handle:
        for line in handle:
            line = line.strip()
            line = line.split('\t')
        
            assert(len(line) == 3)
        
            _, name, fig = line
        
            assert type(fig) == str
        
            figs_to_name[fig] = name

    # load full subsystem names using subsystems2role
    ohai("loading %s" % ops['role'])
    name_to_ss = {}
    with open(ops['role']) as handle:
        for line in handle:
            line = line.strip()
            line = line.split('\t')
        
            assert(len(line) == 4)
        
            a, c, b, d = line[1], line[2], line[0], line[3]
        
            name_to_ss[d] = [a, b, c]

    # Print table, using SEED headers
    ohai("loading %s" % ops['seed'])
    
    handle = open(ops['seed'])
    records = dnaio.Dna(handle)
    
    if ops['out']:
        out = open(ops['out'], 'w')
    else:
        out = sys.stdout

    for record in records:
        header = record.header
    
        fig = header.split()[0]
        original_name = ' '.join(header.split()[1:])
        name = figs_to_name.get(fig, fig)
    
        ss = name_to_ss.get(name, 'NA')
    
        if ss == 'NA':
            names = 'NA;NA;NA;%s;%s' % (original_name, fig)
        else:
            names = '%s;%s;%s;%s;%s' % (ss[0], ss[1], ss[2], name, fig)
        
        names = names.replace(' ','_') #blast, whitespace, blah
    
        record.header = names
        if len(record) != 0:
            print >> out, record.fasta


if __name__ == '__main__':
    main()