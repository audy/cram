# For using SMALT reference assembler

from helps import *
import os

def smalt_index(**ops):
    ''' build reference index '''
    reference = ops['reference']
    name      = ops['name']
    
    cmd = 'smalt index %s %s' % (name, reference)
    run(cmd, generates='%s.smi' % name)

def smalt_map(**ops):
    ''' reference assemble using smalt '''
    
    query     = ops['query']
    reference = ops['reference']
    identity  = ops['identity']
    out       = ops['out']
    threads   = ops.get('threads', 8)
    
    if type(query) is str:
        query_ops = '-q %s' % ops['query']
    elif type(query) in (list, tuple):
        raise Exception, 'currently SMALT can only deal with one reference at a time'
    
    # reference assemble creating .cigar files
    
    cmd = 'smalt map -n %s -y %s -o %s %s %s > /dev/null' % (threads, identity, out, reference, query)
    
    run(cmd, generates=out)
    
def smalt_coverage_table(**ops):
    ''' generate coverage table from smalt cigar output '''
    # this should be easy :)
    
    assembly = ops['assembly']
    phmmer   = ops['phmmer']
    out      = ops['out']

    # TODO add skip if completed

    from collections import defaultdict
    coverage = defaultdict(int)
    
    with open(assembly) as handle:
        for line in handle:
            line = line.split()
            target = line[6]
            coverage[target] += 1

    # load phmmer output table to get figids from ORF names
    target_to_figid = {}
    with open(phmmer) as handle:
        for line in handle:
            if line.startswith('#'): continue
            line = line.strip().split()

            figid, target = line[0], line[2]

            assert target not in target_to_figid

            target_to_figid[target] = figid

    # print coverage table
    with open(out) as handle:
        for target in coverage:
            figid = target_to_figid.get(target, target)
            print >> handle, "%s\t%s" % (figid, coverage[figid])
