# For using SMALT reference assembler
# encoding: utf-8

from runner import *
from logger import *
import os
import sys

def make_sub_names(s):
    ''' Creates list of subsystem combinations
    
    >>> make_sub_names('A;B;C;D')
    ['A', 'A;B', 'A;B;C', 'A;B;C;D']
    
     '''
    if type(s) == str:
        subsystems = s.split(';')
    elif type(s) in (list, tuple):
        subsystems = s
    
    a = []
    for i in range(len(subsystems)+1)[1:]:
        a.append(';'.join(subsystems[0:i]))
    return a

def smalt_index(**ops):
    ''' Build reference index of target sequences
    Required by SMALT prior to reference assembly.
    
    Example: create an index from a set of reference sequences
    
    >>> smalt_index(
    ... reference = '../test/taxcollector.fa',
    ... name      = '../test/tc_index')
     ✓ complete
     
    '''
    reference = ops['reference']
    name      = ops['name']
    
    cmd = '~/cram/bin/smalt index %s %s > /dev/null' % (name, reference)
    run(cmd, generates='%s.smi' % name)

def smalt_map(**ops):
    ''' Perform reference assembly using SMALT
    Requires index of target sequences built by smalt_index()
    
    Example:
    
     >>> smalt_map(
     ... query     = '../test/test.fasta',
     ... reference = '../test/tc_index',
     ... identity  = 0.8,
     ... out       = '../test/smalt_sample_out.txt',
     ... threads   = 2, # default/max = 8
     ... l         = le or mp or False (paired end type, see smalt documentation)
     ... )
      ✓ complete
    '''
    
    query     = ops['query']
    reference = ops['reference']
    identity  = ops['identity']
    out       = ops['out']
    threads   = ops.get('threads', 8)
    l         = ops.get('l', False)
    
    if type(query) is str:
        query_ops = '-q %s' % ops['query']
    elif type(query) in (list, tuple):
        raise Exception, 'currently SMALT can only deal with one reference at a time'
    
    # reference assemble creating .cigar files
    cmd = [
        '~/cram/bin/smalt map',
        '-n %s' % threads,
        '-y %s' % identity,
        '-o %s' % out,
    ]
    
    # for paired-end assemblies
    if l: cmd.append('-l %s' % l)
    
    cmd.append('%s' % reference)
    cmd.append('%s' % query)
    
    # be quiet (really, this should get logged somewhere)
    cmd.append('> /dev/null')
    
    cmd = ' '.join(cmd)
    
    run(cmd, generates=out)
    

def smalt_coverage_table(**ops):
    ''' Takes the cigar-format output of SMALT and generates a coverage table.
    
    Example:
    
    >>> smalt_coverage_table(
    ... # your reference assembly from SMALT
    ... assembly = 'assembly.cigar',
    ...
    ... # you can use phmmer:
    ... phmmer = 'phmmer_table.txt',
    ...
    ... # or blast:
    ... blast = 'blast_table.txt'
    ... # (but not both)
    ...
    ... # output is list of ORF names
    ... # (whatever is in header) and their coverage
    ... out = 'output.txt'
    ... )
    
    '''
    
    ohai('generating coverage table from SMALT assembly')
    assembly = ops['assembly']
    phmmer   = ops.get('phmmer', False)
    blast    = ops.get('blast', False)
    seed     = ops['seed']
    assert (phmmer or blast)
    out      = ops['out']

    # skip if already completed
    if os.path.exists(out):
        okay('skipping')
        return

    from collections import defaultdict
    coverage = defaultdict(int)
    combined_coverage = defaultdict(int)
   
    # measure orf coverage from SMALT assembly
    with open(assembly) as handle:
        for line in handle:
            line = line.split()
            target = line[5]
            coverage[target] += 1

    # load phmmer output table to get figids from ORF names
    target_to_figid = {}
    if phmmer:
        raise Exception, "haven't fixed phmmer but this should be easy."
        with open(phmmer) as handle:
            for line in handle:
                if line.startswith('#'): continue
                line = line.strip().split()
                figid, target = line[0], line[2]
                assert target not in target_to_figid
                target_to_figid[target] = figid
                
    # load blastp output to get subsystem names from ORF names
    # also, get combinations of subsystem names, count coverage for
    # all of them (I'm having a hard time explaining what this does. Just
    # see make_sub_names())
    elif blast:
        with open(blast) as handle:
            for line in handle:
                if line.startswith('#'): continue
                line = line.split()
                target, names = line[0], line[1].split(';')[0:-1]
                
                for name in make_sub_names(names):
                    combined_coverage[name] += coverage[target]
    
    # print combined coverage table
    with open(out, 'w') as handle:
        for name in combined_coverage:
            count = combined_coverage[name]
            print >> handle, "%s\t%s" % (name, count)
        

if __name__ == '__main__':
    # clean up
    files = [
        '../test/tc_index*',
        '../test/smalt_sample_out.txt' ]
    for f in files:
        run('rm -f %s' % f, silent=True)
    
    import doctest
    doctest.testmod()
