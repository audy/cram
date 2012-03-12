import os
from dnaio import *

def get_outdir(out):
    ''' Create a function to add output directory to a given directory
    
    >>> d_func = get_outdir('test')
    >>> print d_func('another_directory')
    test/another_directory
    
    '''
    def s(s):
        # TODO make sure directories exist and if not, make them
        return os.path.join(out, s)
    return s

def split_fasta(**kwargs):
    ''' split a fasta file into x fasta files with n records '''
    
    infile  = kwargs['infile']
    out_dir = kwargs['out_dir']
    n       = int(kwargs['n'])
    format  = kwargs.get('format', 'fasta')
    
    run('mkdir -p %s' % out_dir)
    
    i, j = 0, 0
    with open(infile) as handle:
        out_handle = False
        for record in Dna(handle, type='fasta'):
            if not out_handle or (i >= n):
                i = 0
                j += 1
                ohai('splitting orfs: %s' % j)
                out_handle = open('%s/%s.%s' % (out_dir, j, format), 'w')
            print >> out_handle, record
            i += 1