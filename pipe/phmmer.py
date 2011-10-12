# encoding: utf-8

from helps import *

def phmmer(**ops):
    ''' Runs phmmer.
    # This fails because of relative directory bull-ish. Gotta fix this.
    # >>> phmmer(
    # ... query = '../test/test.fasta',
    # ... db    = '../test/sample_seed.faa',
    # ... out   = '../test/test_phmmer.out' )
    # ✪ running phmmer: ../test/test.fasta vs. ../test/sample_seed.fna
    # ✓ complete
    '''
    
    # phmmer doesn't like to use as many cpus as you specify
    # so it would be a good idea to put some kind of simple
    # map reduce in here,  ala: from concurrent.futures import *
    
    # phmmer is slow when it comes to threading. I don't think has
    # anything to do with Disk IO as it's still slow even with a
    # ram disk. I may have to use some kind of map-reduce to speed
    # this up.
    
    phmmer = ' '.join([
        '~/cram/bin/phmmer',
        '--notextw',
        '--domE 0.001',
        '--incE 0.00001',
        '--cpu 24',
        '--incdomE 0.00001',
        '--noali',
        '-o /dev/null',
        '--tblout %(out)s.table',
        '-E 0.00001',
        #'/dev/stdin',
        '%(query)s',
        '%(db)s'
    ]) % ops
    
    ohai('running phmmer: %(query)s vs. %(db)s' % ops)
    run(phmmer, generates=ops['out'] + '.table')
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()