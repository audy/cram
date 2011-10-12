# For using SMALT reference assembler
# encoding: utf-8

from helps import *
import os

def smalt_index(**ops):
    ''' build reference index
    
    # create an index from a set of reference sequences
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
    ''' reference assemble using smalt
     
     >>> smalt_map(
     ... query     = '../test/test.fasta',
     ... reference = '../test/tc_index',
     ... identity  = 0.8,
     ... out       = '../test/smalt_sample_out.txt',
     ... threads   = 2, # default/max = 8
     ... )
      ✓ complete
    '''
    
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
    cmd = ' '.join([
        '~/cram/bin/smalt map',
        '-n %s' % threads,
        '-y %s' % identity,
        '-o %s' % out,
        '%s' % reference,
        '%s' % query,
        '> /dev/null'])
    
    run(cmd, generates=out)
    

def smalt_coverage_table(**ops):
    ''' generate coverage table from smalt cigar output '''
    
    ohai('Generating coverage table from SMALT assembly')
    assembly = ops['assembly']
    phmmer   = ops.get('phmmer', False)
    out      = ops['out']

    # skip if already completed
    if os.path.exists(out):
        okay('skipping')
        return

    from collections import defaultdict
    coverage = defaultdict(int)
   
    # measure orf coverage
    with open(assembly) as handle:
        for line in handle:
            line = line.split()
            target = line[5]
            coverage[target] += 1

    # load phmmer output table to get figids from ORF names
    target_to_figid = {}
    if phmmer:
        with open(phmmer) as handle:
            for line in handle:
                if line.startswith('#'): continue
                line = line.strip().split()
                figid, target = line[0], line[2]
                assert target not in target_to_figid
                target_to_figid[target] = figid

    # print coverage table
    with open(out, 'w') as handle:
        for target in coverage:
            # Get figid from target (ORF id)
            # Keep ORF name if unidentified.
            figid = target_to_figid.get(target, target)
            reads = coverage.get(target, 0)
            print >> handle, "%s\t%s" % (figid, reads)


if __name__ == '__main__':
    # clean up
    files = [
        '../test/tc_index*',
        '../test/smalt_sample_out.txt' ]
    for f in files:
        run('rm -f %s' % f, silent=True)
    
    import doctest
    doctest.testmod()
